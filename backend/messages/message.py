class Message:
    def __init__(self, role, content, id=None, tokens=None):
        self.role = role
        self.content = content
        self.id = id
        self.tokens = tokens

    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'id': self.id,
            'tokens': self.tokens
        }