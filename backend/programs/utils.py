import pytz
from datetime import datetime
from importlib import import_module
from backend.models import ProgramRegistryModel, UserModel

"""
Shared program utilities
"""

async def get_local_time_str():
    user = await UserModel.first()
    if user.profile and 'timezone' in user.profile:
        local_tz = pytz.timezone(user.profile['timezone'])
        local_time = datetime.now(local_tz)
        local_time_iso = local_time.isoformat()
        day = local_time.strftime('%A')

        return f"It is {day}. The local date and time is: {local_time_iso}."
    else:
        return False

def get_program_ref(class_name: str):
    """
    This function returns a reference to the program class based on the class name.
    """
    module = import_module("backend.programs")
    class_ref = getattr(module, class_name)
    return class_ref

async def get_select_options():
    """
    This function fetches all program options from the database, along with their metadata, and returns formatted values in a list.
    """
    program_registries = await ProgramRegistryModel.all().values("class_name", "display_name", "description", "icon")
    programs = [{"option": pr['display_name'], "value": pr['class_name'], "description": pr['description'], "icon": pr['icon']} for pr in program_registries if pr['class_name'] != 'DefaultProgram']
    return programs