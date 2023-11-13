from io import BytesIO
import datetime
import pytz

from pyowm import OWM

from backend.plugins import BasePlugin, snippet, tool


class Essentials(BasePlugin):
    def __init__(self, id, conversation_id, services, settings=None, data=None):
        super().__init__(id, conversation_id, services, settings, data)

        if "notepad" not in self.data:
            self.data["notepad"] = []

    @snippet
    async def insert_date_time(self, context):
        profile_tz = self.services.get_profile_field("timezone")
        settings_tz = self.settings["insert_date_time"]["timezone"]

        timezone = settings_tz if settings_tz else profile_tz

        if timezone:
            local_tz = pytz.timezone(timezone)
            local_time = datetime.datetime.now(local_tz)
            local_time_str = local_time.isoformat()
            day = local_time.strftime("%A")

            context.add_snippet(
                f"It is {day}. The local date and time in {timezone} is: {local_time_str}."
            )
        else:
            utc_time = datetime.datetime.now(pytz.timezone("UTC"))
            utc_time_str = utc_time.isoformat()
            day = utc_time.strftime("%A")

            context.add_snippet(
                f"Important! The user's timezone is not currently set. You should offer to set the `timezone` field in tz database format for them using the `update_profile_tool` (if available). The current date and time in UTC is: {utc_time_str}."
            )

    @snippet
    async def insert_local_weather(self, context):
        credentials = self.services.get_credentials("openweathermap")

        if credentials is None:
            await self.services.send_alert_to_ui(
                "OpenWeatherMap integration is required", "error"
            )

        # First try to get a location from plugin settings, then from profile
        profile_location = self.services.get_profile_field("location")
        plugin_location = self.settings["insert_local_weather"]["location"]
        location = plugin_location if plugin_location else profile_location

        owm = OWM(credentials["api_key"])

        if location:
            try:
                mgr = owm.weather_manager()
                observation = mgr.weather_at_place(location)
                weather = observation.weather

                temp = weather.temperature("fahrenheit")
                status = weather.detailed_status

                context.add_snippet(
                    f"It's {round(temp['temp'])} degrees Fahrenheit and {status} in {location}."
                )
            except Exception as e:
                print(e)
                await self.services.send_alert_to_ui(
                    "Weather error! Check location and API key.", "error"
                )
        else:
            await self.services.send_alert_to_ui(
                "The Local Weather snippet requires a location!", "error"
            )

    """
    Make & insert custom notes
    """

    @snippet
    async def insert_notes(self, context):
        if len(self.data["notepad"]) > 0:
            notes_str = "The following is your Notepad. These are helpful notes you left for yourself. Refer to these as needed:\n\n"
            for note in self.data["notepad"]:
                notes_str += f"- {note}\n\n"
            context.add_snippet(notes_str)
        else:
            context.add_snippet("Your notepad is currently empty!")

    @tool
    async def make_a_note(self, text):
        if text:
            self.data["notepad"].append(text)
            self.save_state()
        return "Your note has been saved!"

    @tool
    async def clear_notes(self):
        self.data["notepad"] = []
        self.save_state()
        import time

        time.sleep(2)  # Add a delay of 2 seconds

        return "Notepad cleared."

    """
    Updating & insert user profile
    """

    @snippet
    async def insert_user_profile(self, context):
        user_profile = self.services.get_profile()

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
    async def update_user_profile(self, **kwargs):
        existing_profile = self.services.get_profile()

        # Check if the 'fields' key is present in kwargs, since function calling is inconsistent
        if "fields" in kwargs:
            profile_fields = kwargs["fields"]
        else:
            profile_fields = kwargs

        if existing_profile:
            self.services.set_profile({**existing_profile, **profile_fields})
        else:
            self.services.set_profile(profile_fields)

        return "The user's profile was updated!"

    @tool
    async def create_text_file(self, text, filename=None, extension="txt"):
        # Create a file_obj from the text
        file_obj = BytesIO(text.encode())
        # Save the file and get the file info
        file_info = self.services.save_file(file_obj, filename, extension)
        # Return the file info
        await self.services.send_file_to_ui(
            file_info["filename"],
            file_info["filesize"],
            file_info["url"],
            self.conversation_id,
        )
        return f"File saved to {file_info['filepath']}"
