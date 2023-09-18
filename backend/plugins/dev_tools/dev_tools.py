from pathlib import Path
from pydantic import ValidationError
import toml

from backend.services import MessageHandler
from backend.plugins import BasePlugin, tool
from backend.plugins.schema import *

"""
Add function descriptions as doc strings
Access set settings in functions
"""

class DevTools(BasePlugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    @tool
    async def generate_plugin_files(self, plugin_name, display_name, description, author, icon=None, url=None):
        # Define the base directory relative to the current file's location
        base_dir = Path(__file__).parent

        # Create a directory in the plugins directory called plugin_name
        plugins_dir = base_dir.parent
        new_plugin_dir = plugins_dir / plugin_name

        # Check if directory exists
        if new_plugin_dir.exists():
            return f"A directory already exists with the name {plugin_name}. Please choose a new name."
        
        # Create directory
        new_plugin_dir.mkdir(parents=True, exist_ok=True)

        # Read the plugin template
        with open(base_dir / 'templates/plugin.py', 'r') as f:
            plugin_template = f.read()

        # Replace PluginClassName with the formatted name of the plugin name
        plugin_class_name = plugin_name.replace('_', ' ').title().replace(' ', '')
        plugin_template = plugin_template.replace('PluginClassName', plugin_class_name)

        # Save the plugin.py file as plugin_name.py in the new plugin folder
        with open(new_plugin_dir / f"{plugin_name}.py", 'w') as f:
            f.write(plugin_template)

        # Read in templates/plugin.toml
        with open(base_dir / 'templates/plugin.toml', 'r') as f:
            toml_template = f.read()

        # Replace the values in the [metadata] section
        toml_template = toml_template.replace('display_name = ""', f'display_name = "{display_name}"')
        toml_template = toml_template.replace('description = ""', f'description = "{description}"')
        toml_template = toml_template.replace('icon = ""', f'icon = "{icon}"')
        toml_template = toml_template.replace('author = ""', f'author = "{author}"')
        toml_template = toml_template.replace('url = ""', f'url = "{url}"')

        # Save the plugin.toml file as `plugin.toml` in the new plugin directory
        with open(new_plugin_dir / "plugin.toml", 'w') as f:
            f.write(toml_template)

        return f"Plugin created at: `{new_plugin_dir}`"


    @tool
    async def generate_snippet(self, name, display_name, description, settings=None):
        message_handler = MessageHandler()
        try:
            # Prepare the data
            data = {
                'display_name': display_name,
                'description': description,
            }
            
            if settings:
                # Convert settings list to dictionary
                settings_dict = {setting['name']: setting for setting in settings}
                data['settings'] = settings_dict

            # Validate and parse the data using the Snippet schema
            config_instance = Snippet(**data)
            
            # Export the pydantic model instance back to a dictionary
            config_dict = config_instance.dict(exclude_unset=True)

            # Convert the dictionary to a TOML string
            toml_string = toml.dumps({"snippets": {name: config_dict}})
            toml_config = f"# Snippet: {display_name}\n\n" + toml_string
            response = f"Here's your snippet configuration:\n\n```\n{toml_config}```"

            # Prepare the function template 
            function_template = f"""
            @snippet
            async def {name}(self, context):
                \"\"\"
                {description}
                \"\"\"

                # Your snippet logic here
                output = \"...\""""

            # Show the user how to access the settings
            if settings:
                for setting in settings:
                    function_template += f"\n    # {setting['name']} = self.settings['{name}']['{setting['name']}']"

            function_template += """

                # Add your output string to context
                context.add_snippet(output)
            """

            # Add the function template to the response
            response += f"\n\nAnd here's your function template:\n\n```python{function_template}\n```"

            await message_handler.send_message_to_ui(response, self.conversation.id)
            return toml_string
        except ValidationError as e:
            await message_handler.send_message_to_ui(e, self.conversation.id)
            return f"Error creating new snippet: {e}"


    @tool
    async def generate_tool(self, name, display_name, description, llm_description, parameters, settings=None):
        message_handler = MessageHandler()
        try:
            # Prepare the data
            data = {
                'display_name': display_name,
                'description': description,
                'llm_description': llm_description,
            }
            
            if parameters:
                # Convert parameters list to dictionary
                parameters_dict = {parameter['name']: parameter for parameter in parameters}
                data['parameters'] = parameters_dict
            
            # Convert settings list to dictionary or create an empty one
            settings_dict = {setting['name']: setting for setting in settings} if settings else {}

            # Add required settings
            settings_dict['requires_approval'] = {
                'description': 'Require user approval before running tool',
                'value': True,
                'type': 'boolean',
                'editable': True
            }
            settings_dict['follow_up_on_output'] = {
                'description': 'Generate a new response to tool output',
                'value': True,
                'type': 'boolean',
                'editable': False
            }

            data['settings'] = settings_dict

            # Validate and parse the data using the Tool schema
            config_instance = Tool(**data)
            
            # Export the pydantic model instance back to a dictionary
            config_dict = config_instance.dict(exclude_unset=True)

            # Convert the dictionary to a TOML string
            toml_string = toml.dumps({"tools": {name: config_dict}})
            toml_config = f"# Tool: {display_name}\n\n" + toml_string
            response = f"Here's your tool configuration:\n\n```\n{toml_config}```"

            type_mapping = {"string": "str", "integer": "int", "boolean": "bool", "float": "float", "double": "float"}
            function_signature = ",\n".join([f"    {param['name']}: {type_mapping.get(param['type'], param['type'])}" for param in parameters])

            # Prepare the function template 
            function_template = f"""
            @tool
            async def {name}(self,
            {function_signature}):
                \"\"\"
                {description}
                \"\"\"

                # Your tool logic here
                output = \"...\""""

            function_template += """

                # Return tool output as a string
                return output
            """

            # Add the function template to the response
            response += f"\n\nAnd here's your function template:\n\n```python{function_template}\n```"

            await message_handler.send_message_to_ui(response, self.conversation.id)
            return response
        except ValidationError as e:
            await message_handler.send_message_to_ui(e, self.conversation.id)
            return f"Error creating new tool: {e}"
