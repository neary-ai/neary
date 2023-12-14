import google.generativeai as genai

from typing import Union
from .llm_interface import LLMInterface
from ..schemas import ChatModel
from config import settings
from modules.messages.schemas import AssistantMessage, AlertMessage, Content


class GoogleAI(LLMInterface):
    def __init__(self, llm_settings=None, message_handler=None):
        self.llm_settings = llm_settings
        self.message_handler = message_handler
        self.create_client()

        self.model = GoogleAIModel(llm_settings, message_handler)

    def get_models(self):
        chat_models = []
        for m in self.client.list_models():
            if 'generateContent' in m.supported_generation_methods:
                chat_models.append(ChatModel(api="googleai", model=m.name))

        return chat_models

    def create_client(self):
        api_key = settings.chat_models.get("googleai_api_key", None)
        genai.configure(api_key=api_key)
        self.client = genai

    async def create_chat(self, context, conversation_id, functions=None, stream=True) -> Union[AssistantMessage, None]:
        try:
            model_name = self.llm_settings.get('model', 'gemini-pro')
            model = self.client.GenerativeModel(model_name)
            messages = self.model.format_messages(context)
            params = self.model.generate_params(messages, functions, stream)

            if stream:
                response = await model.generate_content_async(**params)
                collected_text = ""
                async for chunk in response:
                    collected_text += chunk.text

                    ai_message = AssistantMessage(
                        conversation_id=conversation_id,
                        content=Content(text=collected_text),
                        status="incomplete",
                    )
                    await self.message_handler.send_message_to_ui(
                        ai_message,
                        save_to_db=False,
                    )
                
                ai_message.status = "complete"

                await self.message_handler.send_message_to_ui(
                    ai_message,
                    save_to_db=True,
                )
            else:
                response = model.generate_content(**params)
                ai_message = AssistantMessage(
                    conversation_id=conversation_id,
                    content=Content(text=response.text),
                    status="complete",
                )
                await self.message_handler.send_message_to_ui(
                    ai_message,
                    save_to_db=True,
                )
            return ai_message

        except Exception as e:
            print(type(e))
            print(e)
            if 'prompt_feedback' in str(e):
                error_message = "Your message was blocked by the model's safety filter."
            else:
                error_message = str(e)
                
            message = AlertMessage(content=error_message, type="error")
            await self.message_handler.send_alert_to_ui(message)
            return None


class GoogleAIModel:
    def __init__(self, llm_settings, message_handler):
        self.llm_settings = llm_settings
        self.message_handler = message_handler

    def generate_params(self, messages, functions=None, stream=True):
        # The common parameters across all models
        params = {
            "contents": messages,
            "stream": stream,
            "generation_config": {
                "temperature": self.llm_settings["temperature"],
                "top_p": self.llm_settings.get("top_p", 1),
                "stop_sequences": self.llm_settings.get("stop", None),
                "candidate_count": self.llm_settings.get("n", 1),
                "top_k": self.llm_settings.get("top_k", None)
            }
        }
        
        max_tokens = self.llm_settings.get("max_tokens", None)

        if max_tokens:
            params["max_output_tokens"] = max_tokens

        # Add functions if they exist
        # if functions:
        #     params["tools"] = functions

        return params

    def format_messages(self, context):
        # Get the list of messages formatted for API call
        formatted_chain = []
        snippet_content = ""

        # First pass: compile all snippet content
        for message in context.compiled_chain():
            if message.role == "snippet":
                snippet_content += "\n\n" + message.content.text

        # Second pass: construct the formatted chain
        for message in context.compiled_chain():
            if message.role == "system":
                # Append the snippet_content to the system message content
                # system_message_content = message.content.text + snippet_content
                # formatted_chain.append(
                #     {"role": "user", "parts": [system_message_content]}
                # )
                pass
            elif message.role == "assistant" and message.function_call:
                # Not sure how to handle function calls in this case, so I'm just skipping them
                continue
            elif message.role == "function":
                # Not sure how to handle function calls in this case, so I'm just skipping them
                continue
            elif message.role == "assistant":
                formatted_chain.append(
                    {"role": "model", "parts": [message.content.text]}
                )                
            elif message.role in ["user"]:
                formatted_chain.append(
                    {"role": message.role, "parts": [message.content.text]}
                )

        return formatted_chain