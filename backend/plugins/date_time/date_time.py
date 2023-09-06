import datetime
import pytz

from backend.services import UserProfileManager
from backend.plugins import BasePlugin, snippet

class DateTimeSnippet(BasePlugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

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
