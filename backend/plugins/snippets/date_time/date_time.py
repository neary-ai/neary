from backend.plugins import Snippet
from backend.services import UserProfileManager
import datetime
import pytz

class DateTimeSnippet(Snippet):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    async def run(self, context):
        profile_manager = UserProfileManager()

        timezone = self.settings.get('timezone', await profile_manager.get_field('timezone'))

        if timezone:
            local_tz = pytz.timezone(timezone)
            local_time = datetime.datetime.now(local_tz)
            local_time_iso = local_time.isoformat()
            day = local_time.strftime('%A')

            context.add_snippet(f"It is {day}. The local date and time is: {local_time_iso}.")
        else:
            utc_time = datetime.datetime.now(pytz.timezone('UTC'))
            utc_time_iso = utc_time.isoformat()
            day = utc_time.strftime('%A')

            context.add_snippet(f"It is {day}. The current date and time in UTC is: {utc_time_iso}. The user can set their `timezone` field in their user profile to get the local time.")