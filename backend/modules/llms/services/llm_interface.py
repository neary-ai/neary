from abc import ABC, abstractmethod
from modules.messages.services.message_chain import MessageChain


class LLMInterface(ABC):
    @abstractmethod
    async def create_chat(self):
        pass

    @abstractmethod
    def get_models(self):
        pass