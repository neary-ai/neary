import aiohttp
import asyncio
import requests
import json
from typing import Union
from .llm_interface import LLMInterface
from ..schemas import ChatModel
from config import settings
from modules.messages.schemas import AssistantMessage, AlertMessage, Content

class Ollama(LLMInterface):
    def __init__(self, llm_settings=None, message_handler=None):
        self.llm_settings = llm_settings
        self.message_handler = message_handler
        self.create_client()

    def get_models(self):
        url = f"{self.base_url}/api/tags"
        try:
            response = requests.get(url)
            response.raise_for_status()
            models_data = response.json()
            chat_models = [
                ChatModel(api="ollama", model=model_info['name'])
                for model_info in models_data.get('models', [])
            ]
            return chat_models
        except requests.RequestException as e:
            print(f"No ollama service detected, skipping model import.")
            return []

    def create_client(self):
        self.base_url = settings.chat_models.get("ollama_base_url", "http://localhost:11434")

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
        messages = self.format_messages(context)
        model_name = self.llm_settings["model"]
        try:
            collected_tokens = ""
            async for response_chunk in self.generate_completion(model_name, messages, stream):
                chunk = json.loads(response_chunk)
                if "response" in chunk:
                    collected_tokens += chunk["response"]
                    if not chunk.get("done", False):
                        # Send incomplete message to UI
                        ai_message = AssistantMessage(
                            conversation_id=conversation_id,
                            content=Content(text=collected_tokens),
                            status="incomplete",
                        )
                        await self.message_handler.send_message_to_ui(
                            ai_message,
                            save_to_db=False,
                        )

                if chunk.get("done", False):
                    break

            # Send complete message to UI
            ai_message = AssistantMessage(
                conversation_id=conversation_id,
                content=Content(text=collected_tokens),
                metadata=context.get_metadata(),
                status="complete",
                xray={"messages": context.get_chain_as_dict()},
            )

            await self.message_handler.send_message_to_ui(
                ai_message,
                save_to_db=True,
            )

            return ai_message
        except Exception as e:
            message = AlertMessage(content=str(e), type="error")
            await self.message_handler.send_alert_to_ui(message)
            print(f"An exception occurred: {e}")
            return None

    def format_messages(self, context):
        inst_formatted_chain = ""
        for message in context.compiled_chain():
            if message.role == "user":
                inst_formatted_chain += f"[INST] {message.content.text} [/INST]"
            elif message.role == "assistant":
                inst_formatted_chain += f"\\n{message.content.text}"
        return inst_formatted_chain.strip()
