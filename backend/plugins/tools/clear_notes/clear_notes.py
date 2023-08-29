from backend.plugins import Tool

class ClearNotesTool(Tool):
    
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)
        self.data['notepad'] = self.data.get('notepad', [])

    async def run(self):
        self.data['notepad'] = []
        await self.save_state()

        return "Notepad cleared."