import json
from typing import Union
from openai import AsyncOpenAI

from .llm_interface import LLMInterface
from ..schemas import ChatModel
from config import settings
from modules.messages.schemas import AssistantMessage, AlertMessage, Content


class OpenAI(LLMInterface):
    def __init__(self, llm_settings=None, message_handler=None):
        self.llm_settings = llm_settings
        self.message_handler = message_handler
        self.create_client()

        model = llm_settings["model"] if llm_settings else None
        if model == "gpt-4-vision-preview":
            self.model = VisionModel(llm_settings, message_handler)
        else:
            self.model = OpenAIModel(llm_settings, message_handler)

    def get_models(self):
        models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview", "gpt-4-vision-preview"]
        chat_models = [ChatModel(api="openai", model=model) for model in models]
        return chat_models

    def create_client(self):
        api_key = settings.chat_models.get("openai_api_key", None)
        base_url = "https://api.openai.com/v1"
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def create_chat(
        self, context, conversation_id, functions=None, stream=True
    ) -> Union[AssistantMessage, None]:
        messages = self.model.format_messages(context)
        params = self.model.generate_params(messages, functions, stream)

        for attempt in range(3):
            try:
                response = await self.client.chat.completions.create(**params)

                if not stream:
                    serialized_response = response.model_dump()
                    return serialized_response["choices"][0]["message"]["content"]
                else:
                    collected_tokens = ""
                    function_name = ""
                    function_arguments = ""
                    async for response_chunk in response:
                        try:
                            chunk = response_chunk.model_dump()
                            delta = chunk["choices"][0]["delta"]

                            if delta:
                                collected_tokens += delta.get("content", "") or ""
                                function_call = delta.get("function_call")

                                if function_call:
                                    function_name = (
                                        function_call.get("name") or function_name
                                    )
                                    function_arguments += (
                                        function_call.get("arguments", "") or ""
                                    )

                            ai_message = AssistantMessage(
                                conversation_id=conversation_id,
                                content=Content(text=collected_tokens),
                                status="incomplete",
                            )

                            await self.message_handler.send_message_to_ui(
                                ai_message,
                                save_to_db=False,
                            )
                        except Exception as e:
                            print("Error in chunk: ", chunk)
                            print(e)

                    function_call = (
                        {
                            "name": function_name,
                            "arguments": json.loads(function_arguments),
                        }
                        if function_name
                        else None
                    )

                    ai_message.status = "complete"
                    ai_message.metadata = context.get_metadata()
                    ai_message.function_call = function_call
                    ai_message.xray = {"messages": context.get_chain_as_dict()}

                    await self.message_handler.send_message_to_ui(
                        ai_message,
                        save_to_db=True,
                    )

                    return ai_message
            except Exception as e:
                message = AlertMessage(content=str(e), type="error")
                await self.message_handler.send_alert_to_ui(message)

                print("An exception occured: ", e)
                return None
        message = AlertMessage(content="Error connecting to chat model", type="error")
        await self.message_handler.send_alert_to_ui(message)
        print("Failed after 3 retries.")
        return None


class OpenAIModel:
    def __init__(self, llm_settings, message_handler):
        self.llm_settings = llm_settings
        self.message_handler = message_handler

    def generate_params(self, messages, functions=None, stream=True):
        # The common parameters across all models
        params = {
            "model": self.llm_settings["model"],
            "messages": messages,
            "temperature": self.llm_settings["temperature"],
            "top_p": self.llm_settings.get("top_p", 1),
            "n": self.llm_settings.get("n", 1),
            "stream": stream,
            "presence_penalty": self.llm_settings.get("presence_penalty", 0),
            "frequency_penalty": self.llm_settings.get("frequency_penalty", 0),
            "stop": self.llm_settings.get("stop", None),
        }

        # Add functions if they exist
        if functions:
            params["functions"] = functions

        # Set max_tokens if it's defined and greater than 0
        max_tokens = self.llm_settings.get("max_tokens", None)
        if max_tokens and max_tokens > 0:
            params["max_tokens"] = max_tokens

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
                system_message_content = message.content.text + snippet_content
                formatted_chain.append(
                    {"role": message.role, "content": system_message_content}
                )
            elif message.role == "assistant" and message.function_call:
                formatted_chain.append(
                    {
                        "role": message.role,
                        "content": None,
                        "function_call": message.function_call,
                    }
                )
            elif message.role == "function":
                formatted_chain.append(
                    {
                        "role": message.role,
                        "content": message.content.text,
                        "name": message.function_call["name"],
                    }
                )
            elif message.role in ["assistant", "user"]:
                formatted_chain.append(
                    {
                        "role": message.role,
                        "content": message.content.text,
                    }
                )
        return formatted_chain


class VisionModel(OpenAIModel):
    def generate_params(self, messages, functions=None, stream=True):
        # Call the parent class's generate_params method to get the common parameters
        params = super().generate_params(messages, functions, stream)

        # Remove the 'stop' parameter for the vision model
        params.pop("stop", None)

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
                system_message_content = message.content.text + snippet_content
                formatted_chain.append(
                    {
                        "role": message.role,
                        "content": [{"type": "text", "text": system_message_content}],
                    }
                )
            elif message.role == "assistant" and message.function_call:
                formatted_chain.append(
                    {
                        "role": message.role,
                        "content": None,
                        "function_call": message.function_call,
                    }
                )
            elif message.role in ["assistant", "user"]:
                content = []
                if message.content.text:
                    content.append({"type": "text", "text": message.content.text})
                if hasattr(message.content, "images") and message.content.images:
                    for image in message.content.images:
                        content.append(
                            {
                                "type": "image_url",
                                "image_url": {"url": f"{image}"},
                            }
                        )
                formatted_chain.append(
                    {
                        "role": message.role,
                        "content": content,
                    }
                )

        return formatted_chain
