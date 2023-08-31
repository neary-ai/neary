from pyowm import OWM

from backend.plugins import BasePlugin, snippet
from backend.services import UserProfileManager, MessageHandler, CredentialManager

class LocalWeather(BasePlugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    @snippet
    async def insert_local_weather(self, context):
        message_handler = MessageHandler()
        profile_manager = UserProfileManager()
        credential_manager = await CredentialManager.create("openweathermap")
        
        credentials = await credential_manager.get_credentials()

        if credentials is None:
             await message_handler.send_alert_to_ui("OpenWeatherMap integration is required", self.conversation.id)

        # First try to get a location from plugin settings, then from profile
        location = self.settings['insert_local_weather'].get('location', await profile_manager.get_field('location'))

        owm = OWM(credentials['api_key'])

        if location:
            try:
                mgr = owm.weather_manager()
                observation = mgr.weather_at_place(location)
                weather = observation.weather

                temp = weather.temperature('fahrenheit')
                status = weather.detailed_status

                context.add_snippet(f"It's {round(temp['temp'])} degrees Fahrenheit and {status} in {location}.")
            except Exception as e:
                print(e)
                await message_handler.send_alert_to_ui("Weather error! Check location and API key.", self.conversation.id)
        else:
            message_handler = MessageHandler()
            await message_handler.send_alert_to_ui("The Local Weather snippet requires a location!", self.conversation.id)