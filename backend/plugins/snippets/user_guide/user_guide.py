import os

from backend.plugins import Snippet

class UserGuideSnippet(Snippet):
    name = "user_guide"
    display_name = "User Guide"
    description = "Inserts the contents of the user guide"

    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    async def run(self, context):
        with open(os.path.join(os.path.dirname(__file__), 'user_guide.md'), 'r') as file:
            user_guide = file.read()
        context.add_snippet(user_guide)