from backend.plugins import BasePlugin, tool, snippet
from backend.services import MessageHandler
from .lib.google_service import GoogleService


class GoogleCalendar(BasePlugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

        self.google_service = GoogleService()

    @snippet
    async def insert_calendar_events(self, context):
        days = self.settings['insert_calendar_events']['days']
        filter_recurring = self.settings['insert_calendar_events']['filter_recurring']
        concise = self.settings['insert_calendar_events']['concise']
        
        try:
            await self.google_service.authenticate()
        except Exception as e:
            print('Error: ', e)
            message_handler = MessageHandler()
            await message_handler.send_alert_to_ui("Invalid Google Calendar credentials", self.conversation.id)
            return

        try:
            events = await self.google_service.get_calendar_events(days=days, filter_recurring=filter_recurring)
        except Exception as e:
            print('Error: ', e)
            message_handler = MessageHandler()
            await message_handler.send_alert_to_ui("Unable to retrieve events. Check your Google Calendar integration.", self.conversation.id)
            return
        
        if events:
            if concise:
                events_strs = [
                    f"{x['summary']} @ {x['start_time']} with {', '.join(x['attendees'])}" for x in events]
                events_str = "\n".join(events_strs)
                context.add_snippet(events_str)
                return events_str
            context.add_snippet(events)
        context.add_snippet("No calendar events for the next 7 days.")

    @tool
    async def create_calendar_event(self, event_title, event_description, start_time, end_time, attendees):
        try:
            await self.google_service.authenticate()        
        except Exception as e:
            print(e)
            message_handler = MessageHandler()
            await message_handler.send_alert_to_ui("Invalid Google Calendar credentials", self.conversation.id)
            return
        
        res = self.google_service.create_calendar_event(event_title, event_description, start_time, end_time, attendees)
        
        if res:
            return "Event created!"
        else:
            return "An error occured while creating the calendar event."
        
    @tool
    async def get_calendar_events(self, days):
        filter_recurring = self.settings['get_calendar_events']['filter_recurring']
        concise = self.settings['get_calendar_events']['concise']
        try:
            await self.google_service.authenticate()        
        except Exception as e:
            print(e)
            message_handler = MessageHandler()
            await message_handler.send_alert_to_ui("Invalid Google Calendar credentials", self.conversation.id)
            return

        events = await self.google_service.get_calendar_events(days=days, filter_recurring=filter_recurring)
        if events:
            if concise:
                events_strs = [f"{x['summary']} @ {x['start_time']} with {', '.join(x['attendees'])}" for x in events]
                events_str = "\n".join(events_strs)
                return events_str
            return events
        return "No calendar events for this period."