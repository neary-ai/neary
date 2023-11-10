import os
import re
import json
import time
import secrets

from sqlalchemy.orm import joinedload, Session
from requests_oauthlib import OAuth2Session

from config import settings
from modules.plugins.models import FunctionModel
from ..models import IntegrationModel, IntegrationInstanceModel


class IntegrationService:
    def __init__(self, db: Session):
        self.db = db

    def get_integrations(self):
        return self.db.query(IntegrationModel).all()

    def get_integration_by_id(self, id: int):
        return self.db.query(IntegrationModel).filter(IntegrationModel.id == id).first()

    def get_integration_by_name(self, name: str):
        return (
            self.db.query(IntegrationModel)
            .filter(IntegrationModel.name == name)
            .first()
        )

    def update_integration_credentials(
        self, instance: IntegrationInstanceModel, credentials: dict
    ):
        instance.credentials = credentials
        self.db.commit()

    def get_credentials(self, integration_name):
        integration = self.get_integration_by_name(integration_name)
        instance = self.get_integration_instance(integration)

        if instance is None:
            return None

        credentials = instance.credentials

        if integration.auth_method == "oauth":
            oauth_handler = OAuthHandler(integration)

            # Check if the token is expired or about to expire
            if (
                "expires_at" in credentials
                and credentials["expires_at"] - time.time() < 300
            ):  # less than 5 minutes to expiry
                # Refresh the token
                new_credentials = oauth_handler.refresh_access_token(credentials)

                # Update the credentials in the database
                instance.credentials = new_credentials

                self.db.commit()

                # Return the new access token
                return new_credentials

        # If the token is not expired, return the existing access token
        return credentials

    def get_integration_instance(self, integration: IntegrationModel):
        return (
            self.db.query(IntegrationInstanceModel)
            .filter(IntegrationInstanceModel.integration == integration)
            .first()
        )

    def create_integration_instance(
        self, integration: IntegrationModel, credentials: None
    ):
        instance = IntegrationInstanceModel(
            integration=integration, credentials=credentials
        )
        self.db.add(instance)
        self.db.commit()

        return instance

    def disconnect_integration(self, integration_id: int):
        # Get the instance with related objects
        integration_instance = (
            self.db.query(IntegrationInstanceModel)
            .filter(IntegrationInstanceModel.integration_id == integration_id)
            .options(
                joinedload(IntegrationInstanceModel.integration)
                .joinedload(IntegrationModel.functions)
                .joinedload(FunctionModel.instances)
            )
            .first()
        )

        if integration_instance:
            for function in integration_instance.integration.functions:
                # Delete function instances that require integration
                for instance in function.instances:
                    self.delete_integration_instance(instance)

            self.delete_integration_instance(integration_instance)

    def delete_integration_instance(self, instance: IntegrationInstanceModel):
        self.db.delete(instance)
        self.db.commit()

    def load_integrations(self):
        """
        Updates available integrations to match config file
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)

        with open(os.path.join(parent_dir, "integrations.json"), "r") as f:
            integrations = json.load(f)

        # Replace placeholders with values from settings.toml
        for integration in integrations:
            for key, value in integration["data"].items():
                if isinstance(value, str):
                    integration["data"][key] = re.sub(
                        r"\{(.+?)\}",
                        lambda m: settings.get(m.group(1), m.group(0)),
                        value,
                    )

        integration_names = set(integration["name"] for integration in integrations)

        db_integrations = self.get_integrations()

        for db_integration in db_integrations:
            if db_integration.name not in integration_names:
                self.db.delete(db_integration)

        for integration in integrations:
            existing_integration = self.get_integration_by_name(integration["name"])
            if existing_integration is None:
                new_integration = IntegrationModel(**integration)
                self.db.add(new_integration)
            else:
                for key, value in integration.items():
                    setattr(existing_integration, key, value)

        self.db.commit()


class OAuthHandler:
    def __init__(self, integration, token=None):
        self.integration = integration
        os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = str(
            settings.APPLICATION.oauthlib_insecure_transport
        )
        self.oauth = OAuth2Session(
            self.integration.data["client_id"],
            scope=self.integration.data["scopes"],
            redirect_uri=self.integration.data["redirect_uri"],
            token=token,
        )

    def get_auth_url(self):
        state = json.dumps(
            {"csrf_token": secrets.token_hex(), "integration_id": self.integration.id}
        )
        auth_url, _ = self.oauth.authorization_url(
            self.integration.data["auth_url"],
            state=state,
            access_type="offline",
            prompt="select_account",
        )
        return auth_url

    def fetch_token(self, authorization_response):
        token = self.oauth.fetch_token(
            self.integration.data["token_url"],
            client_secret=self.integration.data["client_secret"],
            authorization_response=authorization_response,
        )
        return token

    def refresh_access_token(self, current_token):
        # Create an OAuth2Session instance with the current token
        oauth = OAuth2Session(
            self.integration.data["client_id"],
            scope=self.integration.data["scopes"],
            redirect_uri=self.integration.data["redirect_uri"],
            token=current_token,
        )

        # Use the OAuth2Session instance to refresh the token
        new_token = oauth.refresh_token(
            self.integration.data["token_url"],
            client_id=self.integration.data["client_id"],
            client_secret=self.integration.data["client_secret"],
        )

        return new_token
