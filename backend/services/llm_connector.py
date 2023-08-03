import openai
from langchain.callbacks.base import AsyncCallbackHandler

class StreamHandler(AsyncCallbackHandler):
    def __init__(self, context, websocket=None):
        self.context = context
        self.websocket = websocket
        self.collected_tokens = ""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def on_chat_model_start(self, serialized, messages, run_id, parent_run_id=None, tags=None, **kwargs):
        pass

    async def on_llm_new_token(self, token: str, **kwargs):
        self.collected_tokens += token
        ai_response = {
            "role": "assistant",
            "content": self.collected_tokens,
            "conversation_id": self.context.conversation_id,
            "status": "incomplete",
        }

        if self.websocket:
            await self.websocket.send_json(ai_response)
        else:
            print(token)

    async def on_llm_end(self, response, **kwargs):
        ai_response = {
            "role": "assistant",
            "content": self.collected_tokens,
            "conversation_id": self.context.conversation_id,
            "metadata": self.context.metadata,
            "status": "complete",
        }

        if self.websocket:
            await self.websocket.send_json(ai_response)
            print(self.collected_tokens)

    async def on_llm_error(self, error, run_id, parent_run_id, **kwargs):
        if self.websocket:
            await self.websocket.send_json({'role': 'error', 'content': str(error)})
        else:
            print('No websocket!')
        return


async def get_embeddings(doc):
    response = openai.Embedding.create(
    input=doc,
    model="text-embedding-ada-002"
    )
    embeddings = response['data'][0]['embedding']
    return embeddings