import datetime
import pytz

from pyowm import OWM

from backend.services import UserProfileManager, MessageHandler, CredentialManager
from backend.plugins import BasePlugin, snippet, tool


class Essentials(BasePlugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

        if 'notepad' not in self.data:
            self.data['notepad'] = []

    @snippet
    async def insert_date_time(self, context):
        profile_manager = UserProfileManager()
        profile_tz = await profile_manager.get_field('timezone')
        settings_tz = self.settings['insert_date_time']['timezone']

        timezone = settings_tz if settings_tz else profile_tz

        if timezone:
            local_tz = pytz.timezone(timezone)
            local_time = datetime.datetime.now(local_tz)
            local_time_str = local_time.strftime('%Y-%m-%d %I:%M%p')
            day = local_time.strftime('%A')

            context.add_snippet(f"It is {day}. The local date and time in {timezone} is: {local_time_str}.")
        else:
            utc_time = datetime.datetime.now(pytz.timezone('UTC'))
            utc_time_str = utc_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
            day = utc_time.strftime('%A')

            context.add_snippet(f"Important! The user's timezone is not currently set. You should offer to set the `timezone` field in tz database format for them using the `update_profile_tool` (if available). The current date and time in UTC is: {utc_time_str}.")

    @snippet
    async def insert_local_weather(self, context):
        message_handler = MessageHandler()
        profile_manager = UserProfileManager()
        credential_manager = await CredentialManager.create("openweathermap")
        
        credentials = await credential_manager.get_credentials()

        if credentials is None:
             await message_handler.send_alert_to_ui("OpenWeatherMap integration is required", self.conversation.id)

        # First try to get a location from plugin settings, then from profile
        profile_location = await profile_manager.get_field('location')
        plugin_location =  self.settings['insert_local_weather']['location']
        location = plugin_location if plugin_location else profile_location
        
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

    """
    Make & insert custom notes
    """

    @snippet
    async def insert_notes(self, context):
        if len(self.data['notepad']) > 0 :
            notes_str = "The following is your Notepad. These are helpful notes you left for yourself. Refer to these as needed:\n\n"
            for note in self.data['notepad']:
                notes_str += f"- {note}\n\n"
            context.add_snippet(notes_str)
        else:
            context.add_snippet("Your notepad is currently empty!")

    @tool
    async def make_a_note(self, text):
        if text:
            self.data['notepad'].append(text)
            await self.save_state()
        return "Your note has been saved!"

    @tool
    async def clear_notes(self):
        self.data['notepad'] = []
        await self.save_state()
        import time
        time.sleep(2)  # Add a delay of 2 seconds

        return "Notepad cleared."

    """
    Updating & insert user profile
    """

    @snippet
    async def insert_user_profile(self, context):
        profile_manager = UserProfileManager()
        user_profile = await profile_manager.get_profile()

        # Check if there's a user profile and if default values are not blank
        if user_profile and any(user_profile.values()):
            profile_str = "Here is the user's profile. Remember to tailor your answers to their information where applicable:\n\n"
            for k, v in user_profile.items():
                if v:
                    profile_str += f"{k}: {v}\n"
            context.add_snippet(profile_str)
        else:
            context.add_snippet("The user's profile is currently empty!")

    @tool
    async def update_user_profile(self, fields):
        profile_manager = UserProfileManager()
        existing_profile = await profile_manager.get_profile()

        if existing_profile:
            await profile_manager.set_profile({**existing_profile, **fields})
        else:
            await profile_manager.set_profile(fields)

        return "The user's profile was updated!"