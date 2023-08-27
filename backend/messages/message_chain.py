from .message import Message


class MessageChain:
    '''
    Helper class to construct a conversation / message chain to pass to AI
    '''

    def __init__(self, system_message=None, user_message=None, tool_output=None, conversation_id=None):
        self.conversation_id = conversation_id
        self.messages = []
        self.metadata = []

        if system_message:
            self.messages.append(
                Message(role='system', content=system_message))

        self.user_message = Message(
            role="user", content=user_message) if user_message else None

        self.tool_output = Message(
            role="tool_output", content=tool_output) if tool_output else None

    def _compiled_chain(self):
        # Return the complete list of messages including the user and tool messages
        compiled_chain = list(self.messages)
        if self.tool_output:
            compiled_chain += [self.tool_output]
        if self.user_message:
            compiled_chain += [self.user_message]
        return compiled_chain

    def get_chain(self):
        # Public method to get the complete list of messages
        return self._compiled_chain()

    def get_chain_as_dict(self):
        # Get the list of messages as a list of dictionaries
        to_dict = [message.to_dict() for message in self._compiled_chain()]
        return to_dict

    def get_precompiled_chain(self):
        # Get the list of messages without the user message and/or tool output
        return self.messages

    def get_formatted_chain(self):
        # Get the list of messages formatted for API call (only system, assistant, user roles)
        formatted_chain = []
        for message in self._compiled_chain():
            if message.role == 'tool_output':
                # Convert 'tool_output' role to 'user' and prepend the appropriate string
                formatted_chain.append(
                    {'role': 'user', 'content': "Tool output: " + message.content})
            elif message.role == 'snippet':
                # Convert 'snippet' role to 'user' and prepend the appropriate string
                formatted_chain.append(
                    {'role': 'user', 'content': "The user provided the following snippet for your context: \n\n" + message.content})
            elif message.role in ['system', 'assistant', 'user']:
                formatted_chain.append(
                    {'role': message.role, 'content': message.content})
        return formatted_chain

    def add_system_message(self, message, id=None, tokens=None, index=None):
        # Add a system message to the list if there is no existing system message
        if any(x.role == 'system' for x in self.messages):
            return
        system_message = Message(
            role='system', content=message, id=id, tokens=tokens)
        self.messages.insert(0, system_message)

    def add_user_message(self, message, id=None, tokens=None, index=None):
        # Add a user message to the list at a specified index or at the end
        if message:
            message_object = Message(
                role='user', content=message, id=id, tokens=tokens)
            if index is not None:
                self.messages.insert(index, message_object)
            else:
                self.messages.append(message_object)

    def add_ai_message(self, message, id=None, tokens=None, index=None):
        # Add an assistant message to the list at a specified index or at the end
        if message:
            ai_message = Message(
                role='assistant', content=message, id=id, tokens=tokens)
            if index is not None:
                self.messages.insert(index, ai_message)
            else:
                self.messages.append(ai_message)

    def add_tool_output(self, message, id=None, tokens=None, index=None):
        # Add tool output to the list at a specified index or at the end
        if message:
            tool_output = Message(role='tool_output',
                                  content=message, id=id, tokens=tokens)
            if index is not None:
                self.messages.insert(index, tool_output)
            else:
                self.messages.append(tool_output)

    def add_snippet(self, message, id=None, tokens=None, index=None):
        # Add snippet to the list at a specified index or at the end
        if message:
            snippet = Message(role='snippet', content=message,
                              id=id, tokens=tokens)
            if index is not None:
                self.messages.insert(index, snippet)
            else:
                self.messages.append(snippet)

    def add_metadata(self, metadata):
        # Add metadata to the list
        self.metadata.append(metadata)

    def get_metadata(self):
        # Return current metadata
        return self.metadata

    def get_user_message(self):
        # Get the current user message
        if self.user_message:
            return self.user_message.content
        return None
