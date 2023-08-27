import time
from tortoise.exceptions import DoesNotExist

from backend.models import IntegrationInstanceModel, IntegrationRegistryModel
from backend.services.oauth_handler import OAuthHandler

class CredentialManager:
    def __init__(self, integration):
        self.integration = integration
        self.oauth_handler = None

        if self.integration.auth_method == 'oauth':
            self.oauth_handler = OAuthHandler(integration)

    @classmethod
    async def create(cls, integration_name):
        try:
            integration = await IntegrationRegistryModel.get(name=integration_name)
        except DoesNotExist:
            raise ValueError(f"Integration with name '{integration_name}' does not exist.")
        return cls(integration)

    async def get_credentials(self):
        instance = await IntegrationInstanceModel.get(integration=self.integration)
        credentials = instance.credentials

        # Check if the token is expired or about to expire
        if self.oauth_handler and credentials['expires_at'] - time.time() < 300:  # less than 5 minutes to expiry
            # Refresh the token
            new_credentials = self.oauth_handler.refresh_access_token(credentials)

            # Update the credentials in the database
            instance.credentials = new_credentials
            await instance.save()

            # Return the new access token
            return new_credentials

        # If the token is not expired, return the existing access token
        return credentials
