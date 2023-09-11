import os
import importlib
import inspect
from toml import load

from backend.models import PluginRegistryModel
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
                    # Load the plugin's config
                    config = load(os.path.join('plugins', plugin_name, 'plugin.toml'))

                    config['metadata']['name'] = plugin_name

                    # Store the plugin class and config in the plugins dict
                    self.plugins[plugin_name] = {'class': cls, 'functions': {}, 'metadata': config['metadata']}

                    # Register the plugin's snippets and tools
                    self.register_decorated_methods(cls, plugin_name, config)

            # Update registry with plugin info
            await self.update_registry(config)

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

        # Update tools and snippets
        functions = {key: value for key, value in config.items() if key != 'metadata'}
        plugin.functions = functions

        await plugin.save()

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

        # Create a copy of function's config
        function_config = config[name].copy()
        function_settings = function_config.pop('settings', {})
        self.plugins[plugin_name]['functions'].setdefault(function_type, {})[name] = {
            'method': method,
            'settings': function_settings
        }
        # Add the function metadata
        self.plugins[plugin_name]['functions'][function_type][name].update(function_config)


    def get_plugin(self, plugin_name):
        return self.plugins[plugin_name]