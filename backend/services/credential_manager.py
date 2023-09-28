import time

from backend.services import integration_service
from backend.services.oauth_handler import OAuthHandler
from backend.database import SessionLocal

class CredentialManager:
    def __init__(self):
        self.integration = None
        self.oauth_handler = None
        self.db = SessionLocal()

    async def get_credentials(self, integration_name):
        try:
            self.integration = integration_service.get_integration_by_name(self.db, name=integration_name)
        except:
            raise ValueError(f"Integration with name '{integration_name}' does not exist.")
        
        instance = integration_service.get_integration_instance(self.db, integration=self.integration)
        
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
                    integration_service.update_integration_credentials(self.db, instance, new_credentials)

                    # Return the new access token
                    return new_credentials

        # If the token is not expired, return the existing access token
        return credentials
