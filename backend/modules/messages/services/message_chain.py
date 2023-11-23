import json
import base64
from PIL import Image
from io import BytesIO

from ..schemas import (
    UserMessage,
    AssistantMessage,
    SystemMessage,
    FunctionMessage,
    SnippetMessage,
)


class MessageChain:
    """
    Helper class to construct a conversation / message chain to pass to AI
    """

    def __init__(
        self,
        system_message: str = None,
        user_message: UserMessage = None,
        function_message: FunctionMessage = None,
        conversation_id: int = None,
    ):
        self.conversation_id = conversation_id
        self.messages = []
        self.metadata = []

        if system_message:
            self.messages.append(SystemMessage(content={"text": system_message}))

        self.user_message = self._process_user_message(user_message)
        self.function_message = function_message

    def compiled_chain(self):
        compiled_chain = list(self.messages)
        if self.function_message:
            compiled_chain += [self.function_message]
        if self.user_message:
            compiled_chain += [self.user_message]
        return compiled_chain

    def get_chain(self):
        # Public method to get the complete list of messages
        return self.compiled_chain()

    def get_chain_as_dict(self):
        # Get the list of messages as a list of dictionaries
        to_dict = [message.model_dump() for message in self.compiled_chain()]
        return to_dict

    def get_chain_as_plain_text(self):
        # Get the message chain as a single plain text string with roles
        plain_text_chain = ""
        for message in self.compiled_chain():
            if "text" in message.content:
                plain_text_chain += f"{message.role.upper()}: {message.content.text}\n"
        return plain_text_chain.strip()

    def get_precompiled_chain(self):
        # Get the list of messages without the user message and/or tool output
        return self.messages

    def add_system_message(self, message, id=None, tokens=None, index=None):
        # Add a system message to the list if there is no existing system message
        if any(x.role == "system" for x in self.messages):
            return
        system_message = SystemMessage(content=message, id=id, tokens=tokens)
        self.messages.insert(0, system_message)

    def add_user_message(self, message, id=None, tokens=None, index=None):
        # Add a user message to the list at a specified index or at the end
        if message:
            message_object = UserMessage(content=message, id=id, tokens=tokens)
            if index is not None:
                self.messages.insert(index, message_object)
            else:
                self.messages.append(message_object)

    def add_ai_message(
        self, message, function_call=None, id=None, tokens=None, index=None
    ):
        # Add an assistant message to the list at a specified index or at the end
        if message or function_call:
            if function_call:
                function_call["arguments"] = json.dumps(function_call["arguments"])

            ai_message = AssistantMessage(
                content=message,
                function_call=function_call,
                id=id,
                tokens=tokens,
            )
            if index is not None:
                self.messages.insert(index, ai_message)
            else:
                self.messages.append(ai_message)

    def add_function_message(
        self, message, function_call, id=None, tokens=None, index=None
    ):
        # Add function/tool output to the list at a specified index or at the end
        if message:
            function_message = FunctionMessage(
                content=message, function_call=function_call, id=id, tokens=tokens
            )
            if index is not None:
                self.messages.insert(index, function_message)
            else:
                self.messages.append(function_message)

    def add_snippet(self, message, id=None, tokens=None, index=None):
        # Add snippet to the list at a specified index or at the end
        if message:
            snippet = SnippetMessage(content={"text": message}, id=id, tokens=tokens)
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

    def _process_user_message(self, user_message):
        if (
            user_message
            and hasattr(user_message.content, "images")
            and user_message.content.images
        ):
            for i, image in enumerate(user_message.content.images):
                # Resize base64 string
                user_message.content.images[i] = self._resize_image(image)
        return user_message

    def _resize_image(self, base64_string, max_size=(768, 768)):
        # Extract data and image format from base64 string
        header, base64_encoded = base64_string.split(",", 1)
        img_format = header.split(";")[0].split("/")[
            1
        ]  # "data:image/png;base64" => "png"

        # Convert base64 string to bytes
        img_data = base64.b64decode(base64_encoded)
        img = Image.open(BytesIO(img_data))

        # Only resize if the image is larger than max_size
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size)  # Resize while maintaining aspect ratio

        # Convert the image back to base64 string
        buffered = BytesIO()
        img.save(buffered, format=img_format)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"data:image/{img_format};base64,{img_str}"
