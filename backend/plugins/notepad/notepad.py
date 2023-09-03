from backend.plugins import BasePlugin, tool, snippet

class Notepad(BasePlugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

        if 'notepad' not in self.data:
            self.data['notepad'] = []

    @snippet
    async def insert_notes(self, context):
        if len(self.data['notepad']) > 0 :
            notes_str = "The following is your Notepad. These are helpful notes you left for yourself. Refer to these as needed:\n\n"
            for note in self.data['notepad']:
                notes_str += f"- {note}\n\n"
            context.add_snippet(notes_str)
        else:
            context.add_snippet("Your notepad is currently empty!")

    @tool
    async def make_a_note(self, text):
        if text:
            self.data['notepad'].append(text)
            await self.save_state()
        return "Your note has been saved!"

    @tool
    async def clear_notes(self):
        self.data['notepad'] = []
        await self.save_state()
        import time
        time.sleep(2)  # Add a delay of 2 seconds

        return "Notepad cleared."