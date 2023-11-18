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
