from backend.plugins import Tool

class ClearNotesTool(Tool):
    name = "clear_notes"
    display_name = "Clear Notes"
    description = "Clears Neary's saved notes."
    llm_description = "`clear_notes`: Erases your saved notes. Only use when instructed by the user. Takes no arguments."
    
    requires_approval = True
    follow_up_on_output = False
    
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

        self.data['notepad'] = self.data.get('notepad', [])

    async def run(self):
        self.data['notepad'] = []
        await self.save_state()

        return "Notepad cleared."