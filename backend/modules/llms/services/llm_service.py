from sqlalchemy.orm import Session
from typing import List

from ..schemas import ChatModel
from .ollama import Ollama
from .openai import OpenAI

class LLMFactory:
    @staticmethod
    def create_llm(llm_settings, message_handler):
        provider = llm_settings["api_type"]
        if provider == "openai":
            return OpenAI(llm_settings, message_handler)
        elif provider == "ollama":
            return Ollama(llm_settings, message_handler)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

class LLMService:
    def __init__(self, db: Session):
        self.db = db

    def get_models(self) -> List[ChatModel]:
        models = OpenAI().get_models()
        models += Ollama().get_models()
        return models