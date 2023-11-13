from typing import TYPE_CHECKING

import tiktoken
from sqlalchemy.orm import Session

from modules.conversations.models import ConversationModel
from modules.messages.schemas import UserMessage, FunctionMessage, AssistantMessage
from modules.plugins.services.plugin_service import PluginService
from modules.messages.services.message_chain import MessageChain
from modules.messages.services.message_service import MessageService
from .conversation_service import ConversationService

if TYPE_CHECKING:
    from core.services.message_handler import MessageHandler


class ChatService:
    def __init__(self, db: Session, message_handler: "MessageHandler"):
        self.db = db
        self.message_handler = message_handler

    async def handle_message(
        self,
        conversation_id: int,
        user_message: UserMessage = None,
        function_message: FunctionMessage = None,
    ):
        continue_conversation = True

        while continue_conversation:
            # Generate context from conversation
            conversation = ConversationService(self.db).get_conversation_by_id(
                conversation_id
            )

            context = await self.generate_context(
                conversation, user_message, function_message
            )

            # Get tool function definitions
            functions = PluginService(self.db).get_tool_definitions(
                conversation.plugins
            )

            # Send to LLM for response
            ai_response = await self.message_handler.get_ai_response(
                conversation, context, functions
            )

            metadata = context.get_metadata()

            # Save messages to database
            message_service = MessageService(self.db)

            if user_message:
                user_message.metadata = metadata
                message_service.create_message(**user_message.model_dump())
            else:
                function_message.metadata = metadata
                message_service.create_message(**function_message.model_dump())

            follow_up_requested = False

            if ai_response:
                message_service.create_message(**ai_response.model_dump())
                function_message, follow_up_requested = await self.handle_tool_request(
                    ai_response, conversation
                )

            if follow_up_requested:
                user_message = None
            else:
                return ai_response, context

    async def generate_context(
        self,
        conversation: ConversationModel,
        user_message: UserMessage = None,
        function_message: FunctionMessage = None,
    ) -> MessageChain:
        # Create new MessageChain object to hold context
        system_message = conversation.settings["llm"]["system_message"]

        context = MessageChain(
            system_message=system_message,
            user_message=user_message,
            function_message=function_message,
            conversation_id=conversation.id,
        )

        # Add snippets output to context
        await PluginService(self.db).add_snippets_to_context(context, conversation)

        # Fill remaining tokens with conversation context
        self.add_conversation_to_context(context, conversation)

        return context

    def add_conversation_to_context(
        self, context: "MessageChain", conversation: ConversationModel
    ):
        # Generate remaining context from past messages
        sorted_messages = ConversationService(self.db).get_conversation_messages(
            conversation
        )

        tokenizer = tiktoken.encoding_for_model("gpt-4")

        token_count = 0

        for message in context.get_chain():
            tokens = len(list(tokenizer.encode(message.content)))
            message.tokens = tokens
            token_count += tokens

        # Insert context messages before we append the user's message
        insert_index = len(context.get_precompiled_chain())

        max_input_tokens = conversation.settings["max_input_tokens"]

        for message in sorted_messages:
            if (
                not message.content
                and not message.function_call
                and not message.metadata
            ):
                continue

            new_message_tokens = len(list(tokenizer.encode(message.content)))

            if token_count + new_message_tokens > max_input_tokens:
                break

            if message.role == "user":
                context.add_user_message(
                    message.content,
                    id=message.id,
                    tokens=new_message_tokens,
                    index=insert_index,
                )
            elif message.role == "assistant":
                context.add_ai_message(
                    message.content,
                    function_call=message.function_call,
                    id=message.id,
                    tokens=new_message_tokens,
                    index=insert_index,
                )
            elif message.role == "function":
                context.add_function_message(
                    message.content,
                    function_call=message.function_call,
                    id=message.id,
                    tokens=new_message_tokens,
                    index=insert_index,
                )
            elif message.role == "system":
                context.add_system_message(
                    message.content,
                    id=message.id,
                    tokens=new_message_tokens,
                    index=1,
                )
            else:
                continue

            token_count += new_message_tokens

        print(f"Final request: {token_count} tokens.")

    async def handle_tool_request(
        self, ai_response: AssistantMessage, conversation: ConversationModel
    ):
        """
        Entry point for tool requests, used after each AI response
        """
        if ai_response.function_call:
            tool_name = ai_response.function_call["name"]
            tool_args = ai_response.function_call["arguments"]

            plugin_service = PluginService(self.db, self.message_handler)

            return await plugin_service.execute_tool(tool_name, tool_args, conversation)

        return None, False
