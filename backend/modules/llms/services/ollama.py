import aiohttp
import asyncio
import json
from typing import Union
from .llm_interface import LLMInterface
from config import settings
from modules.messages.schemas import AssistantMessage


class Ollama(LLMInterface):
    def __init__(self, llm_settings, message_handler):
        self.llm_settings = llm_settings
        self.message_handler = message_handler
        self.base_url = "http://localhost:11434"  # Assuming local server

    async def generate_completion(self, model_name, prompt, stream=True):
        data = {"model": model_name, "prompt": prompt, "stream": stream}
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate", data=json.dumps(data), headers=headers
            ) as resp:
                async for line in resp.content.iter_any():
                    yield line

    async def create_chat(
        self,
        context,
        conversation_id,
        functions=None,
        stream=True,
    ) -> Union[AssistantMessage, None]:
        try:
            messages = self.format_messages(context)
            params = {
                "model": self.llm_settings["model"],
                "prompt": messages,
                "raw": True,
                "stream": stream,
            }

            collected_tokens = ""
            async for response_chunk in self.generate_completion(
                params["model"], params["prompt"], params["stream"]
            ):
                chunk = json.loads(response_chunk)
                if "response" in chunk:
                    collected_tokens += chunk["response"]
                    if not chunk.get("done", False):
                        # Send incomplete message to UI
                        await self.message_handler.send_message_to_ui(
                            message=collected_tokens,
                            conversation_id=conversation_id,
                            status="incomplete",
                            save_to_db=False,
                        )
                if chunk.get("done", False):
                    break

            # Send complete message to UI
            ai_message = AssistantMessage(
                conversation_id=conversation_id,
                content=collected_tokens,
                metadata=context.get_metadata(),
                status="complete",
                xray={"messages": context.get_chain_as_dict()},
            )

            await self.message_handler.send_message_to_ui(
                message=ai_message.content,
                conversation_id=ai_message.conversation_id,
                metadata=ai_message.metadata,
                status=ai_message.status,
                xray=ai_message.xray,
                save_to_db=False,
            )

            return ai_message
        except Exception as e:
            await self.message_handler.send_alert_to_ui(message=str(e), type="error")
            print(f"An exception occurred: {e}")
            return None

    def format_messages(self, context):
        inst_formatted_chain = ""
        for message in context.compiled_chain():
            if message.role == "user":
                inst_formatted_chain += f"[INST] {message.content} [/INST]"
            elif message.role == "assistant":
                inst_formatted_chain += f"\\n{message.content}"
        return inst_formatted_chain.strip()
