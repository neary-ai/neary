from backend.models import UserModel

def requires_approval(func):
    """
    Approval decorator for tools. When present, a tool approval request will be triggered before its use.
    """
    func.requires_approval = True
    return func

class CoreTools:
    """
    A general set of tools available to all programs.
    Doc strings are directed at the LLM, because they're used to form tool descriptions in a conversation context.
    """
    def __init__(self):
        pass
    
    @staticmethod
    @requires_approval
    async def make_a_note(conversation, text):
        '''
        "make_a_note": Saves a note to memory for your future reference. Use only when the user asks you to remember something. Takes a `text` argument.
        '''
        if text:
            conversation.program.notepad.append(text)
            await conversation.program.save_state()
        
        return True

    @staticmethod
    @requires_approval
    async def clear_notes(conversation):
        '''
        "clear_notes": Erases your saved notes. Only use when instructed by the user. Takes no arguments.
        '''
        conversation.program.notepad = []
        await conversation.program.save_state()
        
        return True
    
    @staticmethod
    @requires_approval
    async def update_profile(conversation, **kwargs):
        """
        "update_profile": Updates the user's profile with new information. Takes an `info` (json) argument that contains key-value pairs of the information to be added or updated. E.g. {"name": "Joe", "timezone": "America/Denver"}.
        """
        user = await UserModel.first()
        existing_profile = user.profile
        if user.profile:
            user.profile = {**existing_profile, **kwargs}
        else:
            user.profile = kwargs

        await user.save()

        return True