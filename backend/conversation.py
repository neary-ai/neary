from .models.models import ConversationModel, ProgramModel, ProgramRegistryModel, SpaceModel
from .services.documents.document_manager import DocumentManager
from .programs.default_program.default_program import DefaultProgram
from .programs.utils import get_program_ref, get_select_options


class Conversation:

    def __init__(self, message_handler=None):
        self.id = None
        self.title = None
        self.message_handler = message_handler
        self.program = DefaultProgram(self)
        self.document_manager = DocumentManager(self)

    def __str__(self):
        return self.title

    """
    Message handling
    """
    async def handle_message(self, user_message):
        response = await self.program.execute(user_message)
        return response

    """
    Program handling
    """

    async def load_program(self, program_class_str):
        program_class = get_program_ref(program_class_str)

        if program_class is None:
            return "That program doesn't exist!"

        # Load new program
        self.program = program_class(self)
        conversation_model = await ConversationModel.get(id=self.id)

        # Get the ProgramRegistryModel for the given class_name
        program_registry = await ProgramRegistryModel.get(class_name=program_class_str)

        # Create a new ProgramModel using the fetched ProgramRegistryModel
        program_model = await ProgramModel.create(program_info=program_registry)

        self.program.id = program_model.id
        conversation_model.program = program_model
        await conversation_model.save()

        # Save initial program data & settings
        program_model.state = self.program.get_program_data()
        program_model.settings = self.program.get_settings()
        await program_model.save()

        return f"Program '{program_class}' loaded!"

    """
    Utility methods
    """

    async def set_settings(self, settings):
        if 'conversation' in settings:
            conversation_settings = settings['conversation']
            if 'title' in conversation_settings:
                self.title = conversation_settings['title']['value']
            if 'program' in conversation_settings:
                if self.program.__class__.__name__ != conversation_settings['program']['value']:
                    await self.load_program(conversation_settings['program']['value'])
            if 'space' in conversation_settings:
                conversation_model = await ConversationModel.get(id=self.id)
                if conversation_settings['space']['value'] == -1 or conversation_settings['space']['value'] == '':
                    conversation_model.space_id = None
                else:
                    conversation_model.space_id = conversation_settings['space']['value']
                await conversation_model.save()

        if 'program' in settings:
            await self.program.set_settings(settings['program'])

        await self.save_state()

    async def get_settings(self):

        current_space_id, space_options = await self.get_space_options()

        settings = {
            'id': {
                'display_name': None,
                'value': self.id,
                'field': None
            },
            'title': {
                'display_name': 'Title',
                'value': self.title,
                'field': 'TextInput'
            },
            'program': {
                'display_name': None,
                'value': self.program.__str__(),
                'field': None,
                'options': await get_select_options(),
            },
            'space': {
                'display_name': 'Space',
                'value': current_space_id,
                'field': 'Select',
                'options': space_options
            },
        }

        return {"conversation": settings, "program": self.program.get_settings()}

    async def get_space_options(self):
        spaces = await SpaceModel.filter(is_archived=False)
        space_options = [{"option": space.name, "value": space.id}
                         for space in spaces]

        conversation_model = await ConversationModel.get(id=self.id)
        current_space_id = conversation_model.space_id

        return current_space_id, space_options

    async def save_state(self):
        conversation_model = await ConversationModel.get(id=self.id)
        conversation_model.title = self.title
        await conversation_model.save()

    @classmethod
    async def from_json(cls, conversation_data, message_handler):
        instance = cls.__new__(cls)
        instance.id = conversation_data['id']
        instance.title = conversation_data['title']
        instance.document_manager = DocumentManager(instance)
        instance.message_handler = message_handler

        program_class = get_program_ref(conversation_data['program']['name'])
        instance.program = await program_class.from_json(instance, conversation_data['program'])

        return instance
