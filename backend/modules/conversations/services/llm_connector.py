import json
import asyncio
from typing import TYPE_CHECKING

import openai
from openai.error import Timeout, RateLimitError

from ..models import *
from ..schemas import *
from modules.messages.schemas import AssistantMessage
from config import settings

if TYPE_CHECKING:
    from core.services.message_handler import MessageHandler
    from modules.messages.services.message_chain import MessageChain


class LLMConnector:
    def __init__(
        self,
        context: "MessageChain",
        message_handler: "MessageHandler",
        api_type: str = "openai",
    ):
        self.api_type = api_type
        self.message_handler = message_handler
        self.context = context

        # Azure config
        if self.api_type == "azure":
            openai.api_type = api_type
            api_key = settings.chat_models.get("azure_openai_key", None)
            api_base = settings.chat_models.get("azure_openai_endpoint", None)
            api_version = settings.chat_models.get("azure_openai_api_version", None)

            if not api_key or not api_base:
                raise ValueError(
                    "AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT must be set"
                )

            openai.api_key = api_key
            openai.api_base = api_base
            openai.api_version = "2023-05-15" if not api_version else api_version

        # Custom config
        elif self.api_type == "custom":
            api_base = settings.chat_models.get("custom_endpoint", None)

            if not api_base:
                raise ValueError(
                    "CUSTOM_ENDPOINT must be set in environment variables."
                )

            openai.api_base = api_base

        # Default OpenAI config
        else:
            openai.api_key = settings.chat_models.get("openai_api_key", None)
            openai.api_base = "https://api.openai.com/v1"

    async def create_chat(
        self,
        messages,
        conversation_id,
        model="gpt-4",
        temperature=0.7,
        top_p=1,
        n=1,
        stream=True,
        functions=None,
        max_tokens=0,
        stop=None,
        presence_penalty=0,
        frequency_penalty=0,
    ) -> AssistantMessage | None:
        model_key = "deployment_id" if self.api_type == "azure" else "model"
        print(f"\n\nMESSAGES: {messages}\n\n")
        for attempt in range(3):
            try:
                print(f"\n\nUsing model: {model}\n\n")

                params = {
                    model_key: model,
                    "messages": messages,
                    "temperature": temperature,
                    "top_p": top_p,
                    "n": n,
                    "stream": stream,
                    "stop": stop,
                    "presence_penalty": presence_penalty,
                    "frequency_penalty": frequency_penalty,
                }

                if functions:
                    params["functions"] = functions

                if max_tokens and max_tokens > 0:
                    params["max_tokens"] = max_tokens

                response = await openai.ChatCompletion.acreate(**params)
                if not stream:
                    return response["choices"][0]["message"]["content"]
                else:
                    collected_tokens = ""
                    function_name = ""
                    function_arguments = ""
                    async for chunk in response:
                        try:
                            if (
                                "content" in chunk["choices"][0]["delta"]
                                and chunk["choices"][0]["delta"]["content"] is not None
                            ):
                                collected_tokens += chunk["choices"][0]["delta"][
                                    "content"
                                ]
                            if "function_call" in chunk["choices"][0]["delta"]:
                                if (
                                    "name"
                                    in chunk["choices"][0]["delta"]["function_call"]
                                ):
                                    function_name = chunk["choices"][0]["delta"][
                                        "function_call"
                                    ]["name"]
                                if (
                                    "arguments"
                                    in chunk["choices"][0]["delta"]["function_call"]
                                ):
                                    function_arguments += chunk["choices"][0]["delta"][
                                        "function_call"
                                    ]["arguments"]

                            ai_message = AssistantMessage(
                                conversation_id=conversation_id,
                                content=collected_tokens,
                                status="incomplete",
                            )
                            await self.message_handler.send_message_to_ui(
                                message=ai_message.content,
                                conversation_id=ai_message.conversation_id,
                                status=ai_message.status,
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
                    ai_message.metadata = self.context.get_metadata()
                    ai_message.function_call = function_call
                    ai_message.xray = {"messages": self.context.get_chain_as_dict()}

                    await self.message_handler.send_message_to_ui(
                        message=ai_message.content,
                        conversation_id=ai_message.conversation_id,
                        metadata=ai_message.metadata,
                        function_call=ai_message.function_call,
                        status=ai_message.status,
                        xray=ai_message.xray,
                        save_to_db=False,
                    )

                    return ai_message
            except (Timeout, RateLimitError):
                wait_time = 3**attempt
                print(f"Error. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                await self.message_handler.send_alert_to_ui(
                    message=str(e).replace("OpenAI", "chat model"), type="error"
                )
                print("An exception occured: ", e)
                return None

        await self.message_handler.send_alert_to_ui(
            message="Error connecting to chat model!", type="error"
        )
        print("Failed after 3 retries.")
        return None


async def get_embeddings(doc):
    openai.api_key = settings.chat_models.get("openai_api_key", None)
    response = openai.Embedding.create(input=doc, model="text-embedding-ada-002")
    embeddings = response["data"][0]["embedding"]
    return embeddings
