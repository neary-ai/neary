import os
import asyncio
from backend.programs.tools import requires_approval
from backend.messages import MessageChain
from backend.memory import BaseMemory
from backend.models import UserModel
from ..base_program import BaseProgram

class SupportChat(BaseProgram):

    def __init__(self, conversation):
        super().__init__(conversation)

        self.system_message = "You are an assistant called Neary. Your job is to welcome people to the new Neary app. You should answer questions they have about the service and on-board them by saving their name and timezone (using tz database format) to their profile using the `update_profile` tool. Important: You should never make up an answer. If the user asks you a question about the app that you do not know, or cannot find from contextual information provided to you, simply say you are not sure."

        self.memory_config = {
            "memory_mode": "truncate",
            "token_limit": 5000,
        }
        self.memory = BaseMemory(self)
        
        self.register_tool("update_profile", self.update_profile)
        
        self.toolbox = ['update_profile']

    async def execute(self, user_message):
        messages = MessageChain(system_message=self.system_message, user_message=user_message, conversation_id=user_message['conversation_id'])
        messages.user_msg(await self.get_profile_str())
        messages.user_msg(self.get_tools_str())

        # Use remaining tokens to provide context prior messages in the conversation
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
    async def update_profile(self, **kwargs):
        """
        "update_profile": Updates the user's profile with new information. Takes an `info` (json) argument that contains key-value pairs of the information to be added or updated. E.g. {"name": "Joe", "timezone": "America/Denver"}.
        """
        user = await UserModel.first()
        existing_profile = user.profile
        if user.profile:
            user.profile = {**existing_profile, **kwargs}
        else:
            user.profile = kwargs

        # Reload the UI with updated profile info
        await self.conversation.message_handler.send_command_to_ui(message="reload", conversation_id=self.conversation.id)
        
        if not user.onboarded:
            asyncio.create_task(self.send_onboarding_guide())
            user.onboarded = True
        await user.save()

        return True

    """
    Utility methods
    """

    async def send_onboarding_guide(self):
        # We wait a couple of seconds before sending welcome message so it's not too jarring :)
        await asyncio.sleep(2)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'onboarding_guide.md'), 'r') as text:
            message = text.read()
            await self.memory.save_message({'role': 'assistant', 'content': message, 'conversation_id': self.conversation.id})
            await self.conversation.message_handler.send_message_to_ui(message=message, conversation_id=self.conversation.id)