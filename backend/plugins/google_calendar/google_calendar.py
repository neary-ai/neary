from backend.plugins import BasePlugin, tool, snippet
from .lib.google_service import GoogleService


class GoogleCalendar(BasePlugin):
    def __init__(self, id, conversation_id, services, settings=None, data=None):
        super().__init__(id, conversation_id, services, settings, data)

        access_token = self.services.get_credentials("google_calendar")
        self.google_service = GoogleService(access_token=access_token)

    @snippet
    async def insert_calendar_events(self, context):
        days = self.settings["insert_calendar_events"]["days"]
        filter_recurring = self.settings["insert_calendar_events"]["filter_recurring"]
        concise = self.settings["insert_calendar_events"]["concise"]

        try:
            await self.google_service.authenticate()
        except Exception as e:
            print("Error: ", e)
            await self.services.send_alert_to_ui(
                "Invalid Google Calendar credentials", self.conversation_id
            )
            return

        try:
            events = await self.google_service.get_calendar_events(
                days=days, filter_recurring=filter_recurring
            )
        except Exception as e:
            print("Error: ", e)
            await self.services.send_alert_to_ui(
                "Unable to retrieve events. Check your Google Calendar integration.",
                self.conversation_id,
            )
            return

        if events:
            if concise:
                events_strs = [
                    f"{x['summary']} @ {x['start_time']} with {', '.join(x['attendees'])}"
                    for x in events
                ]
                events_str = "\n".join(events_strs)
                context.add_snippet(
                    f"Here's the user's calendar for the next {days} day(s):\n{events_str}"
                )
                return events_str
            context.add_snippet(events)
        context.add_snippet("No calendar events for the next 7 days.")

    @tool
    async def create_calendar_event(
        self, event_title, event_description, start_time, end_time, attendees=[]
    ):
        try:
            self.google_service.authenticate()
        except Exception as e:
            print(e)
            await self.services.send_alert_to_ui(
                "Invalid Google Calendar credentials", self.conversation_id
            )
            return "Unable to create calendar event. Invalid Google Calendar credentials. The user should ensure their Google Calendar integration is setup correctly."

        res = self.google_service.create_calendar_event(
            event_title, event_description, start_time, end_time, attendees
        )

        if res:
            return "Event created!"
        else:
            return "An error occured while creating the calendar event."

    @tool
    async def get_calendar_events(self, days):
        filter_recurring = self.settings["get_calendar_events"]["filter_recurring"]
        concise = self.settings["get_calendar_events"]["concise"]
        try:
            await self.google_service.authenticate()
        except Exception as e:
            print(e)
            await self.services.send_alert_to_ui(
                message="Invalid Google Calendar credentials"
            )
            return "Unable to retrieve calendar events. Invalid Google Calendar credentials. The user should ensure their Google Calendar integration is setup correctly."

        events = await self.google_service.get_calendar_events(
            days=days, filter_recurring=filter_recurring
        )
        if events:
            if concise:
                events_strs = [
                    f"{x['summary']} @ {x['start_time']} with {', '.join(x['attendees'])}"
                    for x in events
                ]
                events_str = "\n".join(events_strs)
                return events_str
            return events
        return "No calendar events for this period."
