from backend.plugins import Tool

class MakeANoteTool(Tool):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)
        self.data['notepad'] = self.data.get('notepad', [])

    async def run(self, text):
        if text:
            self.data['notepad'].append(text)
            await self.save_state()
        return "Your note has been saved!"