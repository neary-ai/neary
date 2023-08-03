from backend.messages import MessageChain
from backend.memory import BaseMemory
from backend.programs.utils import get_local_time_str
from backend.programs.tools import requires_approval

from ..base_program import BaseProgram
from .utils import GoogleService

class CalendarChat(BaseProgram):

    def __init__(self, conversation):
        super().__init__(conversation)
        self.system_message = "Your job is to act as a personal assistant for the user, getting and scheduling events with their calendar as needed. Important: You should never 'guess' when scheduling events. If you are unsure of a detail, such as an invitees email address, ask the user before scheduling the event. Finally, if you don't see the user's timezone provided in any prior messages, you should ask them for their location before you do anything else. Then, update their timezone with the `update_timezone` tool."

        self.memory_config = {
            "memory_mode": "truncate",
            "token_limit": 3000,
        }
        self.memory = BaseMemory(self)
        
        self.register_tool("create_calendar_event", self.create_calendar_event)
        self.register_tool("get_calendar_events", self.get_calendar_events)
        
        self.toolbox = ['make_a_note', 'clear_notes', 'update_profile', 'create_calendar_event', 'get_calendar_events']
        self.google_service = None

    async def execute(self, user_message):
        """
        Before any messages are processed, let's make sure Google OAuth is in place
        """
        auth_response = await self.google_auth()
        if  not auth_response:
            return
        elif type(auth_response) == str:
            actions = [
                {
                    'type': 'link',
                    'name': 'gcal_auth',
                    'label': 'Login with Google',
                    'conversation_id': self.conversation.id,
                    'data': {'url': auth_response},
                },
            ]
            notification = f'Neary needs permission to access your Google Calendar.'
            await self.conversation.message_handler.send_notification_to_ui(notification=notification, conversation_id=self.conversation.id, actions=actions, save_to_db=False)
            
            return

        messages = MessageChain(system_message=self.system_message, user_message=user_message, conversation_id=user_message['conversation_id'])

        local_time_str = await get_local_time_str()
        
        if local_time_str:
            messages.user_msg(local_time_str)
        else:
            messages.user_msg("IMPORTANT! The user does not have a preferred timezone set. You should request their location and add it to their profile with the `update_profile` tool before you use any other tools.")
        
        messages.user_msg(self.get_tools_str())
        messages.user_msg(self.get_notes_str())
        
        context = await self.memory.generate_context(messages)

        ai_response = await self.conversation.message_handler.get_ai_response(context, self.model)

        await self.memory.save_message(user_message)
        await self.memory.save_message(ai_response)

        await self.handle_tool_requests(ai_response)

        return ai_response

    """
    Custom tools
    """
    @requires_approval
    async def create_calendar_event(self, event_title, event_description, start_time, end_time, attendees):
        """
        "create_calendar_event": Creates an event on the user's calendar. Takes `event_title` (string), `event_description` (string), `start_time` (ISO 8601 string), `end_time` (ISO 8601 string) and `attendees` (email addresses in a Python list) arguments.
        """
        if not self.google_service:
            await self.google_auth()

        res = self.google_service.create_calendar_event(event_title, event_description, start_time, end_time, attendees, self.timezone)
        return True
    
    async def get_calendar_events(self, days=7, filter_recurring=True, concise=True):
        """
        "get_calendar_events": Retrieves the user's upcoming calendar events. Takes optional `days` (integer) argument, where `1` would be today's events, `2` would be today's and tomorrow's events, and so on.
        """
        if not self.google_service:
            await self.google_auth()

        events = self.google_service.get_calendar_events(days=days, filter_recurring=filter_recurring)
        if events:
            if concise:
                events_strs = [f"{x['summary']} @ {x['start_time']} with {', '.join(x['attendees'])}" for x in events]
                events_str = "\n".join(events_strs)
                return events_str
            return events
        return None

    """
    Utility methods
    """
    async def google_auth(self):
        auth_url = None
        success = False

        self.google_service = GoogleService()
        try:
            success, auth_url = await self.google_service.authenticate()
        except Exception as e:
            await self.conversation.message_handler.send_notification_to_ui(notification=str(e), conversation_id=self.conversation.id, actions=None, save_to_db=False)
            print (str(e))
            return

        if success:
            return True
        else:
            print("Authorization is required, please visit:", auth_url)
            return auth_url