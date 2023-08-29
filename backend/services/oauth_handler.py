import json
import secrets
from requests_oauthlib import OAuth2Session

class OAuthHandler:
    def __init__(self, integration, token=None):
        self.integration = integration
        self.oauth = OAuth2Session(
            self.integration.data["client_id"],
            scope=self.integration.data["scopes"],
            redirect_uri=self.integration.data["redirect_uri"],
            token = token
        )

    def get_auth_url(self):
        state = json.dumps({
            'csrf_token': secrets.token_hex(),
            'integration_id': self.integration.id
        })
        auth_url, _ = self.oauth.authorization_url(
            self.integration.data['auth_url'],
            state=state,
            access_type="offline",
            prompt="select_account",
        )
        return auth_url

    def fetch_token(self, authorization_response):
        token = self.oauth.fetch_token(
            self.integration.data['token_url'],
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
            token=current_token
        )

        # Use the OAuth2Session instance to refresh the token
        new_token = oauth.refresh_token(
            self.integration.data["token_url"],
            client_id=self.integration.data["client_id"],
            client_secret=self.integration.data["client_secret"]
        )

        return new_token