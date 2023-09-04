import os
import json
import asyncio
import openai
from openai.error import Timeout, RateLimitError


class LLMConnector:
    def __init__(self, context, api_type="openai", api_key=None, api_base=None, api_version=None, websocket=None):
        self.api_type = api_type
        self.websocket = websocket
        self.context = context

        # Azure config
        if self.api_type == "azure":
            openai.api_type = api_type
            api_key = os.getenv(
                "AZURE_OPENAI_KEY") if api_key is None else api_key
            api_base = os.getenv(
                "AZURE_OPENAI_ENDPOINT") if api_base is None else api_base
            api_version = os.getenv(
                "AZURE_OPENAI_API_VERSION") if api_version is None else api_version

            if not api_key or not api_base:
                raise ValueError(
                    "AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT must be set in environment variables.")

            openai.api_key = api_key
            openai.api_base = api_base
            openai.api_version = "2023-05-15" if not api_version else api_version

        # Custom config
        elif self.api_type == "custom":
            api_base = os.getenv(
                "CUSTOM_ENDPOINT") if not api_base else api_base

            if not api_base:
                raise ValueError(
                    "CUSTOM_ENDPOINT must be set in environment variables.")

            openai.api_base = api_base

        # Default OpenAI config
        else:
            openai.api_base = "https://api.openai.com/v1"

    async def create_chat(self, messages, model="gpt-4", temperature=0.7, top_p=1, n=1, stream=True, functions=None, max_tokens=0, stop=None, presence_penalty=0, frequency_penalty=0):
        model_key = "deployment_id" if self.api_type == "azure" else "model"
        for attempt in range(3):
            try:
                # Create a dictionary for the parameters
                params = {model_key: model,
                        'messages': messages,
                        'temperature': temperature,
                        'top_p': top_p,
                        'n': n,
                        'stream': stream,
                        'stop': stop,
                        'presence_penalty': presence_penalty,
                        'frequency_penalty': frequency_penalty}

                if functions:
                    params['functions'] = functions
                
                if max_tokens and max_tokens > 0:
                    params['max_tokens'] = max_tokens

                response = await openai.ChatCompletion.acreate(**params)
                if not stream:
                    return response['choices'][0]['message']['content']
                else:
                    collected_tokens = ""
                    function_name = ""
                    function_arguments = ""
                    async for chunk in response:
                        try:
                            if 'content' in chunk['choices'][0]['delta'] and chunk['choices'][0]['delta']['content'] is not None:
                                collected_tokens += chunk['choices'][0]['delta']['content']
                            if 'function_call' in chunk['choices'][0]['delta']:
                                if 'name' in chunk['choices'][0]['delta']['function_call']:
                                    function_name = chunk['choices'][0]['delta']['function_call']['name']
                                if 'arguments' in chunk['choices'][0]['delta']['function_call']:
                                    function_arguments += chunk['choices'][0]['delta']['function_call']['arguments']
                            ai_message = {'role': 'assistant', 'content': collected_tokens,
                                        'conversation_id': self.context.conversation_id, 'status': 'incomplete'}
                            await self.websocket.send_json(ai_message)
                        except Exception as e:
                            print('Error in chunk: ', chunk)
                            print(e)
                    function_call = {'name': function_name, 'arguments': json.loads(function_arguments)} if function_name else None
                    ai_message['status'] = 'complete'
                    ai_message['metadata'] = self.context.get_metadata()
                    ai_message['xray'] = {'messages': self.context.get_chain_as_dict()}
                    ai_message['function_call'] = function_call
                    await self.websocket.send_json(ai_message)
                    return ai_message
            except (Timeout, RateLimitError):
                wait_time = 3 ** attempt
                print(f"Error. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                if self.websocket:
                    await self.websocket.send_json({'role': 'error', 'content': str(e).replace('OpenAI', 'chat model')})
                print('An exception occured: ', e)
                return None
        if self.websocket:
            await self.websocket.send_json({'role': 'error', 'content': 'Error connecting to chat model'})
        print("Failed after 3 retries.")
        return None


async def get_embeddings(doc):
    response = openai.Embedding.create(
        input=doc,
        model="text-embedding-ada-002"
    )
    embeddings = response['data'][0]['embedding']
    return embeddings
