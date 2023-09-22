import time
from tortoise.exceptions import DoesNotExist

from backend.models import IntegrationInstanceModel, IntegrationRegistryModel
from backend.services.oauth_handler import OAuthHandler

class CredentialManager:
    def __init__(self):
        self.integration = None
        self.oauth_handler = None

    async def get_credentials(self, integration_name):
        try:
            self.integration = await IntegrationRegistryModel.get(name=integration_name)
        except DoesNotExist:
            raise ValueError(f"Integration with name '{integration_name}' does not exist.")
        
        instance = await IntegrationInstanceModel.get_or_none(integration=self.integration)
        
        if instance is None:
            return None
        
        credentials = instance.credentials

        if self.integration.auth_method == 'oauth':
                self.oauth_handler = OAuthHandler(self.integration)

                # Check if the token is expired or about to expire
                if 'expires_at' in credentials and credentials['expires_at'] - time.time() < 300:  # less than 5 minutes to expiry
                    # Refresh the token
                    new_credentials = self.oauth_handler.refresh_access_token(credentials)

                    # Update the credentials in the database
                    instance.credentials = new_credentials
                    await instance.save()

                    # Return the new access token
                    return new_credentials

        # If the token is not expired, return the existing access token
        return credentials
