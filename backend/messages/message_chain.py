import json

from .message import Message


class MessageChain:
    '''
    Helper class to construct a conversation / message chain to pass to AI
    '''

    def __init__(self, system_message=None, user_message=None, function_output=None, conversation_id=None):
        self.conversation_id = conversation_id
        self.messages = []
        self.metadata = []

        if system_message:
            self.messages.append(
                Message(role='system', content=system_message))

        self.user_message = Message(
            role="user", content=user_message) if user_message else None

        self.function_output = Message(
            role="function", name=function_output['name'], content=function_output['output']) if function_output else None

    def _compiled_chain(self):
        # Return the complete list of messages including the user and tool messages
        compiled_chain = list(self.messages)
        if self.function_output:
            compiled_chain += [self.function_output]
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
        # Get the list of messages formatted for API call
        formatted_chain = []
        snippet_content = ""

        # First pass: compile all snippet content
        for message in self._compiled_chain():
            if message.role == 'snippet':
                snippet_content += "\n\n" + message.content

        # Second pass: construct the formatted chain
        for message in self._compiled_chain():
            if message.role == 'system':
                # Append the snippet_content to the system message content
                system_message_content = message.content + snippet_content
                formatted_chain.append(
                    {'role': message.role, 'content': system_message_content})
            elif message.role == 'assistant' and message.function_call:
                formatted_chain.append(
                    {'role': message.role, 'content': None, 'function_call': message.function_call})
            elif message.role == 'function':
                formatted_chain.append(
                    {'role': message.role, 'content': message.content, 'name': message.name})
            elif message.role in ['assistant', 'user']:
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

    def add_ai_message(self, message, function_call=None, id=None, tokens=None, index=None):
        # Add an assistant message to the list at a specified index or at the end
        if message or function_call:
            if function_call:
                function_call['arguments'] = json.dumps(
                    function_call['arguments'])

            ai_message = Message(role='assistant', content=message,
                                 function_call=function_call, id=id, tokens=tokens)
            if index is not None:
                self.messages.insert(index, ai_message)
            else:
                print('final message appended: ', ai_message)
                self.messages.append(ai_message)

    def add_function_message(self, message, name, id=None, tokens=None, index=None):
        # Add function/tool output to the list at a specified index or at the end
        if message:
            function_output = Message(
                role='function', content=message, name=name, id=id, tokens=tokens)
            if index is not None:
                self.messages.insert(index, function_output)
            else:
                self.messages.append(function_output)

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
