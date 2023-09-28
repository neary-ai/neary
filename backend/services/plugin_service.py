from sqlalchemy.orm import Session
from backend import models


def get_plugin_by_name(db: Session, plugin_name: str):
    return db.query(models.PluginRegistryModel).filter(models.PluginRegistryModel.name == plugin_name).first()

def get_active_plugins(db: Session):
    return db.query(models.PluginRegistryModel).all()

def create_or_update_plugin(db: Session, metadata, default_plugins):
    plugin = get_plugin_by_name(db, metadata['name'])

    if plugin is None:
        plugin = models.PluginRegistryModel(name=metadata['name'])
        plugin.is_enabled = True if metadata['name'] in default_plugins else False

    # Update plugin metadata
    plugin.display_name = metadata['display_name']
    plugin.description = metadata['description']
    plugin.icon = metadata.get('icon', None)
    plugin.author = metadata['author']
    plugin.url = metadata['url']
    plugin.version = metadata['version']
    plugin.settings_metadata = metadata.get('settings', None)

    db.add(plugin)
    db.commit()
    db.refresh(plugin)

    return plugin


def delete_plugin(db: Session, plugin: models.PluginRegistryModel):
    db.delete(plugin)
    db.commit()


def save_plugin_instance_state(db: Session, plugin_instance: models.PluginInstanceModel, new_data: dict, new_settings: dict):
    plugin_instance.data = new_data

    function_instances = db.query(models.FunctionInstanceModel).filter(
        models.FunctionInstanceModel.plugin_instance_id == plugin_instance.id).all()

    for function in function_instances:
        if function.name in new_settings:
            for setting_key in new_settings[function.name]:
                function.settings_values[setting_key] = new_settings[function.name][setting_key]

    db.commit()


def create_plugin_instance(db: Session, plugin: dict, conversation: models.ConversationModel):
    plugin_registry = db.query(models.PluginRegistryModel).filter_by(
        name=plugin["name"]).first()
    if plugin_registry:
        plugin_registry.is_enabled = True

        plugin_instance = models.PluginInstanceModel(
            name=plugin["name"], plugin=plugin_registry, settings_values=plugin.get("settings", None), conversation=conversation)
        db.add(plugin_instance)
        db.flush() # Flush to assign an ID to plugin_instance

        for function in plugin["functions"]:
            function_name = function["name"]
            function_details = db.query(models.FunctionRegistryModel).filter_by(
                name=function_name).first()
            if function_details:
                function_instance = models.FunctionInstanceModel(
                    name=function_name, function=function_details, plugin_instance=plugin_instance, settings_values=function.get('settings', None))
                db.add(function_instance)

        db.commit()


def enable_plugin(db: Session, plugin_registry: models.PluginRegistryModel):
    plugin_registry.is_enabled = True
    db.commit()


def remove_function_instances(db: Session, plugin_instance: models.PluginInstanceModel, plugin_functions: list):
    function_instances = plugin_instance.function_instances
    for instance in function_instances:
        if not any(function["name"] == instance.name for function in plugin_functions):
            db.delete(instance)
            db.commit()


def update_function_instances(db: Session, plugin_instance: models.PluginInstanceModel, plugin_functions: list):
    function_instances = plugin_instance.function_instances
    for function in plugin_functions:
        function_name = function["name"]
        settings = function.get('settings') or {}
        settings_values = {key: value['value'] if isinstance(
            value, dict) and 'value' in value else value for key, value in settings.items()}
        existing_function_instance = None
        for instance in function_instances:
            if instance.name == function_name:
                existing_function_instance = instance
        if existing_function_instance:
            existing_function_instance.settings_values = settings_values
            db.commit()
        else:
            function_registry = db.query(models.FunctionRegistryModel).filter_by(
                name=function_name).first()
            if function_registry is None:
                print('Function not found: ', function_name)
                return
            function_instance = models.FunctionInstanceModel(
                name=function_name, function=function_registry, plugin_instance=plugin_instance, settings_values=settings_values)
            db.add(function_instance)
            db.commit()
