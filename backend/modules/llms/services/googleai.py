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

        model = llm_settings["model"] if llm_settings else None
        if model and "vision" in model:
            self.model = GeminiVisionModel(llm_settings, message_handler)
        else:
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
            "safety_settings": {'HARASSMENT':'block_none'}, 
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
        prev_role = None
        prev_parts = []

        # First pass: compile all snippet content
        for message in context.compiled_chain():
            if message.role == "snippet":
                snippet_content += "\n\n" + message.content.text

        # Second pass: construct the formatted chain
        for message in context.compiled_chain():
            if message.role == "system":
                pass
            elif message.role == "assistant" and message.function_call:
                continue
            elif message.role == "function":
                continue
            else:
                if message.role == "assistant":
                    role = "model"
                else:  # message.role == "user"
                    role = "user"
                
                if role == prev_role:  # If the role is the same as the previous one, combine the parts
                    prev_parts.append(message.content.text)
                else:  # If the role is different, append the previous parts to the chain and update the current role and parts
                    if prev_role is not None:
                        formatted_chain.append({"role": prev_role, "parts": prev_parts})
                    prev_role = role
                    prev_parts = [message.content.text]

        # Add the last message to the chain
        if prev_role is not None:
            formatted_chain.append({"role": prev_role, "parts": prev_parts})

        return formatted_chain

class GeminiVisionModel(GoogleAIModel):
    def __init__(self, llm_settings, message_handler):
        self.llm_settings = llm_settings
        self.message_handler = message_handler

    def format_messages(self, context):
        # Get the list of messages formatted for API call
        formatted_chain = []
        snippet_content = ""
        prev_role = None
        prev_parts = []

        # First pass: compile all snippet content
        for message in context.compiled_chain():
            if message.role == "snippet":
                snippet_content += "\n\n" + message.content.text

        # Second pass: construct the formatted chain
        for message in context.compiled_chain():
            if message.role == "system":
                pass
            elif message.role == "assistant" and message.function_call:
                continue
            elif message.role == "function":
                continue
            else:
                if message.role == "assistant":
                    role = "model"
                else:  # message.role == "user"
                    role = "user"
                
                parts = []
                if message.content.text:
                    parts.append({"text": message.content.text})
                if hasattr(message.content, "images") and message.content.images:
                    for image in message.content.images:
                        mime_type, image_data = self._extract_mime_and_data(image)
                        parts.append(
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": image_data,
                                }
                            }
                        )

                if role == prev_role:  # If the role is the same as the previous one, combine the parts
                    prev_parts.extend(parts)
                else:  # If the role is different, append the previous parts to the chain and update the current role and parts
                    if prev_role is not None and prev_parts:
                        formatted_chain.append({"role": prev_role, "parts": prev_parts})
                    prev_role = role
                    prev_parts = parts

        # Add the last message to the chain
        if prev_role is not None and prev_parts:
            formatted_chain.append({"role": prev_role, "parts": prev_parts})

        return formatted_chain

    def _extract_mime_and_data(self, data_url):
        # Split the data URL at the first comma
        mime, data = data_url.split(',', 1)

        # Remove the 'data:' prefix and the ';base64' suffix to get the MIME type
        mime_type = mime[5:-7]

        return mime_type, data