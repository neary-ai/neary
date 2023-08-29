from backend.plugins import Tool
from backend.plugins.utils.google_service import GoogleService
from backend.services import MessageHandler

class CreateCalendarEventTool(Tool):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)
        self.google_service = GoogleService()
    
    async def run(self, event_title, event_description, start_time, end_time, attendees):
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