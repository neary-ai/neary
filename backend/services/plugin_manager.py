import os
import json
import importlib
import inspect
from toml import load
from pydantic import ValidationError
from tortoise.exceptions import DoesNotExist

from backend.models import PluginRegistryModel, IntegrationRegistryModel, FunctionRegistryModel, PresetModel
from backend.plugins.schema import PluginConfig
from backend.plugins import BasePlugin

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class PluginManager(metaclass=Singleton):
    def __init__(self):
        self.plugins = {}
        self.tools = {}
        self.snippets = {}

    async def load_plugins(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        plugins_dir = os.path.join(root_dir, 'plugins')
        
        for plugin_name in os.listdir(plugins_dir):
            if not plugin_name.startswith('_') and os.path.isdir(os.path.join(plugins_dir, plugin_name)):
                await self.load_plugin(plugin_name)

    async def load_plugin(self, plugin_name):
        try:
            # Import the plugin module
            plugin_module = importlib.import_module(f'plugins.{plugin_name}.{plugin_name}')

            # Find the plugin class in the module
            for name, cls in inspect.getmembers(plugin_module):
                if inspect.isclass(cls) and issubclass(cls, BasePlugin) and cls is not BasePlugin:
                    # Load and validate the plugin's config
                    config = load(os.path.join('plugins', plugin_name, 'plugin.toml'))
                    
                    config['metadata']['name'] = plugin_name
                    
                    # Check if 'live' exists and is False, if so, return early
                    if not config['metadata'].get('live', True):
                        plugin = await PluginRegistryModel.get_or_none(name=plugin_name)
                        if plugin:
                            await plugin.delete()
                        print(f'Plugin {plugin_name} has `live` set to `false`; skipping.')
                        return

                    try:
                        validated_config = PluginConfig(**config)
                    except ValidationError as e:
                        print(f'Invalid configuration for plugin {plugin_name}: {e}')
                        return

                    # Store the plugin class and config in the plugins dict
                    self.plugins[plugin_name] = {'class': cls, 'functions': {}, 'metadata': validated_config.metadata.dict(exclude_unset=True)}

                    # Register the plugin's snippets and tools
                    self.register_decorated_methods(cls, plugin_name, validated_config.dict(exclude_unset=True))

            # Update registry with plugin info
            await self.update_registry(validated_config.dict(exclude_unset=True))

            # Load plugin presets
            presets_path = os.path.join('plugins', plugin_name, 'presets.json')
            if os.path.exists(presets_path):
                await self.load_presets(presets_path)

        except Exception as e:
            print(f'Error loading plugin {plugin_name}: {e}')

    async def update_registry(self, config):
        metadata = config["metadata"]

        plugin = await PluginRegistryModel.get_or_none(name=metadata['name'])
        
        default_plugins = ["essentials"]

        if plugin is None:
            plugin = PluginRegistryModel(name=metadata['name'])
            plugin.is_enabled = True if metadata['name'] in default_plugins else False

        # Update plugin metadata
        plugin.display_name = metadata['display_name']
        plugin.description = metadata['description']
        plugin.icon = metadata.get('icon', None)
        plugin.author = metadata['author']
        plugin.url = metadata['url']
        plugin.version = metadata['version']
        plugin.settings_metadata = metadata.get('settings', None)

        await plugin.save()

        # Update plugin functions
        for key, value in config.items():
            if key in ['snippets', 'tools']:
                for function_name, function_details in value.items():
                    function = await FunctionRegistryModel.get_or_none(name=function_name, plugin=plugin)

                    if function is None:
                        function = FunctionRegistryModel(name=function_name, plugin=plugin, type=key[:-1])

                    function_metadata = {}
                    integrations = []
                    
                    # Add settings, parameters and other metadata
                    for details_key, details_value in function_details.items():
                        if details_key == 'settings':
                            function.settings_metadata = details_value
                        elif details_key == 'parameters':
                            function.parameters = details_value
                        elif details_key == 'integrations':
                            integrations = details_value
                        else:
                            function_metadata[details_key] = details_value
                    
                    function.metadata = function_metadata

                    await function.save()
                    
                    # Add integrations
                    for integration_name in integrations:
                        integration = await IntegrationRegistryModel.get_or_none(name=integration_name)
                        if integration:
                            await function.integrations.add(integration)

    def register_decorated_methods(self, cls, plugin_name, config):
        # Get all methods of the plugin class
        methods = inspect.getmembers(cls, predicate=inspect.isfunction)

        # Filter methods decorated with @snippet or @tool
        snippets = [method for method in methods if hasattr(method[1], 'is_snippet')]
        tools = [method for method in methods if hasattr(method[1], 'is_tool')]

        # Register snippets and tools
        for name, method in snippets:
            self.register_function(name, method, plugin_name, config['snippets'], 'snippets')

        for name, method in tools:
            self.register_function(name, method, plugin_name, config['tools'], 'tools')


    def register_function(self, name, method, plugin_name, config, function_type):
        if name not in config:
            print(f"Error: No matching function found in config for {name}")
            return

        # Check if function name already exists
        for plugin in self.plugins.values():
            if name in plugin['functions'].get(function_type, {}):
                print(f"Warning: Function `{name}` in plugin `{plugin_name}` conflicts with an existing function in plugin `{plugin['metadata']['name']}`")
                return

        # Create callable reference with function definition
        function_config = config[name].copy()
        self.plugins[plugin_name]['functions'].setdefault(function_type, {})[name] = {
            'method': method,
            'definition': self.get_function_definition(name, function_config),
        }

    async def load_presets(self, path):
        with open(path, 'r') as f:
            presets = json.load(f)
        
        for preset in presets:
            try:
                existing_preset = await PresetModel.get(name=preset["name"])
            except DoesNotExist:
                await PresetModel.create(**preset)
            else:
                if not existing_preset.is_custom:
                    for key, value in preset.items():
                        setattr(existing_preset, key, value)
                    await existing_preset.save()

    def parse_parameter(self, param_data):
        if param_data['type'] == 'array' and 'items' in param_data:
            items_properties = self.parse_parameter(param_data['items'])
            return {
                "type": 'array',
                "items": items_properties
            }
        elif param_data['type'] == 'object' and 'properties' in param_data:
            properties = {}
            required = []
            for item_name, item_data in param_data['properties'].items():
                if item_data.get('required'):
                    required.append(item_name)
                properties[item_name] = self.parse_parameter(item_data)
            return {
                "type": 'object',
                "properties": properties,
                "required": required
            }
        else:
            return {
                "type": param_data.get('type'),
                "description": param_data.get('description')
            }

    def get_function_definition(self, tool_name, tool_data):
        function_dict = {}
        function_dict['name'] = tool_name
        function_dict['description'] = tool_data.get('llm_description')

        function_dict['parameters'] = {
            "type": "object",
            "properties": {},
            "required": []
        }

        # Iterate over each parameter in the tool
        for param_name, param_data in tool_data.get('parameters', {}).items():
            function_dict['parameters']['properties'][param_name] = self.parse_parameter(param_data)

            # Check if the parameter is required
            if param_data.get('required'):
                function_dict['parameters']['required'].append(param_name)
        
        return function_dict

    def get_plugin(self, plugin_name):
        return self.plugins[plugin_name]