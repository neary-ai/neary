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
        settings_tz = self.settings['insert_date_time']['timezone']['value']

        timezone = settings_tz if settings_tz else profile_tz

        if timezone:
            local_tz = pytz.timezone(timezone)
            local_time = datetime.datetime.now(local_tz)
            local_time_iso = local_time.isoformat()
            day = local_time.strftime('%A')

            context.add_snippet(f"It is {day}. The local date and time in {timezone} is: {local_time_iso}.")
        else:
            utc_time = datetime.datetime.now(pytz.timezone('UTC'))
            utc_time_iso = utc_time.isoformat()
            day = utc_time.strftime('%A')

            context.add_snippet(f"It is {day}. The current date and time in UTC is: {utc_time_iso}. The user can set their `timezone` field in their user profile to get the local time.")