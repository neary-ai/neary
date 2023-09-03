class Message:
    def __init__(self, role, content, function_call=None, name=None, id=None, tokens=None):
        self.role = role
        self.name = name
        self.content = content
        self.function_call = function_call
        self.id = id
        self.tokens = tokens

    def to_dict(self):
        return {
            'role': self.role,
            'name': self.name,
            'content': self.content,
            'function_call': self.function_call,
            'id': self.id,
            'tokens': self.tokens
        }