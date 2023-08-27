from backend.plugins import Snippet

class NotepadSnippet(Snippet):
    name = "notepad"
    display_name = "Notepad"
    description = "Inserts the contents of Neary's notepad"
    
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    async def run(self, context):
        data = self.get_plugin_data('make_a_note')
        
        if data and 'notepad' in data:
            notes_str = "The following is your Notepad. These are helpful notes you left for yourself. Refer to these as needed:\n\n"
            for note in data['notepad']:
                notes_str += f"- {note}\n\n"
            context.add_snippet(notes_str)