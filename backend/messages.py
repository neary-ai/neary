from langchain.schema import AIMessage, HumanMessage, SystemMessage

class MessageChain:
    '''
    Helper class to construct a conversation / message chain to pass to AI
    '''
    def __init__(self, system_message=None, user_message=None, conversation_id=None):
        self.messages = []
        self.metadata = []
        self.user_message = user_message
        self.conversation_id = conversation_id

        if system_message:
            self.messages.append({'role': 'system', 'content': system_message})

    def set_user_message(self, user_message):
        self.user_message = user_message
    
    def unset_user_message(self):
        if self.user_message:
            self.messages.append(self.user_message)
            self.user_message = None

    def _compiled_chain(self):
        return self.messages + [self.user_message]

    def get_chain(self):
        return self._compiled_chain()

    def get_precompiled_chain(self):
        return self.messages

    def get_formatted_chain(self):
        formatted_messages = []
        for message in self._compiled_chain():
            if message['role'] == 'system':
                formatted_messages.append(SystemMessage(content=message['content']))
            if message['role'] == 'user':
                formatted_messages.append(HumanMessage(content=message['content']))
            if message['role'] == 'assistant':
                formatted_messages.append(AIMessage(content=message['content']))
        return formatted_messages

    def get_chain_str(self):
        chain_str = ""
        for message in self._compiled_chain():
            if message['role'] == 'user' or message['role'] == 'assistant' or message['role'] == 'system':
                chain_str += f"{message['role']}: {message['content']}\n\n"
        return chain_str

    def system_msg(self, msg, index=None):
        if any(x['role'] == 'system' for x in self.messages):
            return
        
        self.messages.insert(0, {'role': 'system', 'content': msg})

    def user_msg(self, msg, index=None):
        if msg:
            if index is not None:
                self.messages.insert(index, {'role': 'user', 'content': msg})
            else:
                self.messages.append({'role': 'user', 'content': msg}) 

    def ai_msg(self, msg, index=None):
        if msg:
            if index is not None:
                self.messages.insert(index, {'role': 'assistant', 'content': msg})
            else:
                self.messages.append({'role': 'assistant', 'content': msg})

    def add_metadata(self, metadata):
        self.metadata.append(metadata)