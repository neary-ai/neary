from backend.plugins import Tool
from backend.plugins.utils.google_service import GoogleService
from backend.services import MessageHandler

class GetCalendarEventsTool(Tool):
    name = "get_calendar_events"
    display_name = "Get Calendar Events"
    description = "Retrieves calendar events for a given number of days."
    llm_description = "`get_calendar_events`: Retrieves the user's upcoming calendar events. Takes optional `days` (integer) argument, where `1` would be today's events, `2` would be today's and tomorrow's events, and so on."
    
    integrations = ['google_calendar']
    requires_approval = False
    follow_up_on_output = True
    
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

        self.google_service = GoogleService()

    async def run(self, days=7, filter_recurring=True, concise=True):
        try:
            await self.google_service.authenticate()        
        except Exception as e:
            print(e)
            message_handler = MessageHandler()
            await message_handler.send_alert_to_ui("Invalid Google Calendar credentials", self.conversation.id)
            return

        events = self.google_service.get_calendar_events(days=days, filter_recurring=filter_recurring)
        if events:
            if concise:
                events_strs = [f"{x['summary']} @ {x['start_time']} with {', '.join(x['attendees'])}" for x in events]
                events_str = "\n".join(events_strs)
                return events_str
            return events
        return "No calendar events for this period."