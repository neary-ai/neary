from backend.plugins import Tool

class MakeANoteTool(Tool):
    name = "make_a_note"
    display_name = "Make a Note"
    description = "Saves a note for Neary's future reference"
    llm_description = "`make_a_note`: Saves a note to memory for your future reference. Use only when the user asks you to remember something. Takes a `text` argument."
    
    requires_approval = True
    follow_up_on_output = True
    
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

        self.data['notepad'] = self.data.get('notepad', [])

    async def run(self, text):
        if text:
            self.data['notepad'].append(text)
            await self.save_state()
        return "Your note has been saved!"