import os
import importlib
import inspect
from copy import deepcopy
from toml import load
from backend.plugins import BasePlugin

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            instance.load_plugins()
            cls._instances[cls] = instance
        return cls._instances[cls]

class PluginManager(metaclass=Singleton):
    def __init__(self):
        self.plugins = {}
        self.tools = {}
        self.snippets = {}

    def load_plugins(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        plugins_dir = os.path.join(root_dir, 'plugins')
        
        for plugin_name in os.listdir(plugins_dir):
            if os.path.isdir(os.path.join(plugins_dir, plugin_name)):
                self.load_plugin(plugin_name)

    def load_plugin(self, plugin_name):
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
        
        except Exception as e:
            print(f'Error loading plugin {plugin_name}: {e}')

    def register_decorated_methods(self, cls, plugin_name, config):
        # Get all methods of the plugin class
        methods = inspect.getmembers(cls, predicate=inspect.isfunction)

        # Filter methods decorated with @snippet or @tool
        snippets = [method for method in methods if hasattr(method[1], 'is_snippet')]
        tools = [method for method in methods if hasattr(method[1], 'is_tool')]

        # Register snippets and tools
        for name, method in snippets:
            self.register_function(name, method, plugin_name, config, 'snippet')

        for name, method in tools:
            self.register_function(name, method, plugin_name, config, 'tool')


    def register_function(self, name, method, plugin_name, config, function_type):
        if name not in config[function_type+'s']:
            print(f"Error: No matching {function_type} found in config for {name}")
            return
        # Create a copy of function's config
        function_config = config[function_type+'s'][name].copy()
        function_settings = function_config.pop('settings', {})
        self.plugins[plugin_name]['functions'][name] = {
            'method': method,
            'type': function_type,
            'settings': function_settings
        }
        # Add the function metadata
        self.plugins[plugin_name]['functions'][name].update(function_config)

    def get_plugin(self, plugin_name):
        return self.plugins[plugin_name]

    def get_plugins(self):
        return self.plugins

    def get_serialized_plugins(self):
        serialized_plugins = []
        for plugin_name, plugin in self.plugins.items():
            serialized_plugin = deepcopy(plugin)
            serialized_plugin['name'] = plugin_name
            # Remove the class reference
            del serialized_plugin['class']
            # Create the 'functions' dictionary
            functions = {}
            for function_name, function in serialized_plugin['functions'].items():
                # Check if the 'method' key exists
                if 'method' in function:
                    del function['method']
                else:
                    print(f"Function '{function_name}' in plugin '{plugin_name}' does not have a 'method' key")
                # Add the function to the 'functions' dictionary
                functions[function_name] = function
            # Add the 'functions' dictionary to the plugin
            serialized_plugin['functions'] = functions
            # Add the plugin to the list of serialized plugins
            serialized_plugins.append(serialized_plugin)
        return serialized_plugins

    def add_metadata(self, plugin_instance):
        # Get the plugin from the manager
        functions = plugin_instance.functions
        plugin_name = plugin_instance.name

        plugin = self.plugins[plugin_name]

        # Merge the functions from the model and the manager
        for function_name, function_data in functions.items():
            if function_name in plugin['functions']:
                # Merge the two dictionaries
                merged_function_data = {**function_data, **plugin['functions'][function_name]}
                
                # If 'settings' key exists in both, merge them
                if 'settings' in function_data and 'settings' in plugin['functions'][function_name]:
                    user_settings = function_data['settings'] if function_data['settings'] is not None else {}
                    default_settings = plugin['functions'][function_name]['settings'] if plugin['functions'][function_name]['settings'] is not None else {}
                    
                    # Update only the 'value' key in each setting
                    for setting_name, setting_value in user_settings.items():
                        if setting_name in default_settings:
                            default_settings[setting_name]['value'] = setting_value['value']
                    
                    # Update the merged function data with the updated settings
                    merged_function_data['settings'] = default_settings

                # Remove the method reference
                merged_function_data.pop('method', None)
                
                functions[function_name] = merged_function_data

        return functions, plugin['metadata']