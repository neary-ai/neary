import pytest
from backend.conversation import Conversation
from backend.services import MessageHandler
from backend.models import ConversationModel

@pytest.fixture
def dummy_message_handler():
    class DummyMessageHandler(MessageHandler):
        async def get_ai_response(self, *args, **kwargs):
            response = {'role': 'assistant', 'content': 'Hello! How can I assist you today?', 'conversation_id': 3, 'status': 'complete', 'metadata': [], 'xray': {'messages': [{'role': 'system', 'name': None, 'content': 'You are a helpful assistant.', 'function_call': None, 'id': None, 'tokens': 6}, {'role': 'snippet', 'name': None, 'content': "The user's profile is currently empty!", 'function_call': None, 'id': None, 'tokens': 8}, {'role': 'user', 'name': None, 'content': 'hello', 'function_call': None, 'id': None, 'tokens': 1}]}, 'function_call': None}
            return response

    return DummyMessageHandler()

@pytest.fixture
def conversation(db_session, dummy_message_handler):
    conversation_model = db_session.query(ConversationModel).first()
    serialized = conversation_model.serialize()

    conversation = Conversation(id=serialized['id'], 
                                title=serialized['title'], 
                                settings=serialized['settings'], 
                                plugins=serialized['plugins'], 
                                message_handler=dummy_message_handler,
                                db=db_session)

    conversation.load_plugins()
    
    return conversation

@pytest.mark.asyncio
async def test_conversation_tools(conversation):
    assert len(conversation.tools) > 0

@pytest.mark.asyncio
async def test_conversation_snippets(conversation):
    assert len(conversation.snippets) > 0

@pytest.mark.asyncio
async def test_handle_message_response(conversation):
    ai_response, context = await conversation.handle_message(user_message="Hello!")
    assert ai_response['role'] == 'assistant'

@pytest.mark.asyncio
async def test_message_chain_contains_user_message(conversation):
    ai_response, context = await conversation.handle_message(user_message="Hello!")
    message_chain = context.get_chain_as_dict()
    assert any(message for message in message_chain if message['role'] == 'user' and message['content'] == 'Hello!')
