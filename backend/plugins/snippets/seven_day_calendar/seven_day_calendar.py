from backend.plugins import Snippet
from backend.plugins.utils.google_service import GoogleService

from backend.services import MessageHandler


class SevenDayCalendarSnippet(Snippet):
    name = "seven_day_calendar"
    display_name = "7 Day Calendar"
    description = "Inserts calendar events for the next week."

    integrations = ['google_calendar']

    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

        self.google_service = GoogleService()

    async def run(self, context, days=7, filter_recurring=True, concise=True):
        try:
            await self.google_service.authenticate()
        except Exception as e:
            message_handler = MessageHandler()
            await message_handler.send_alert_to_ui("Invalid Google Calendar credentials", self.conversation.id)
            return

        events = self.google_service.get_calendar_events(
            days=days, filter_recurring=filter_recurring)
        if events:
            if concise:
                events_strs = [
                    f"{x['summary']} @ {x['start_time']} with {', '.join(x['attendees'])}" for x in events]
                events_str = "\n".join(events_strs)
                context.add_snippet(events_str)
                return events_str
            context.add_snippet(events)
        context.add_snippet("No calendar events for the next 7 days.")
