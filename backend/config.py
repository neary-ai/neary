import os
import json
import importlib.util
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.contrib.fastapi import register_tortoise
import importlib.util
from backend.models import PluginRegistryModel, PresetModel, IntegrationRegistryModel, Migration
from backend.plugins import Snippet
from backend.plugins import Tool

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "data/db.sqlite3")
db_url = f"sqlite:///{db_path}"


async def run_setup(app):
    # Initialize ORM
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["backend.models.models"]}
    )

    # Apply migrations, if necessary
    # await apply_migrations()
    await Tortoise.generate_schemas()

    # Register ORM with FastAPI
    register_tortoise(
        app,
        db_url=db_url,
        modules={"models": ["backend.models.models"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )

    await load_plugins()
    await load_presets()
    await load_integrations()


async def apply_migrations():
    """
    Apply necessary migrations to bring DB up-to-date
    """
    migration_files = sorted(os.listdir(
        os.path.join(base_dir, "models/migrations")))
    for migration_file in migration_files:
        if migration_file.endswith('.py'):
            # Import the migration module
            spec = importlib.util.spec_from_file_location(
                "migration", os.path.join(base_dir, "models/migrations", migration_file))
            migration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration)

            try:
                # Check if the migration has been applied
                await Migration.get(name=migration_file)
            except (DoesNotExist, OperationalError):
                # If not, apply the migration
                sql_script = await migration.upgrade(Tortoise.get_connection('default'))
                await Tortoise.get_connection('default').execute_script(sql_script)

                await Migration.create(name=migration_file)

                print(f"Migration applied: {migration_file}")


async def load_plugins():
    # Set all plugins to inactive
    await PluginRegistryModel.all().update(is_active=False)

    plugin_dirs = ["plugins/snippets", "plugins/tools"]

    # List all directories in the plugin directories
    for plugin_dir in plugin_dirs:
        for dir_name in os.listdir(plugin_dir):
            dir_path = os.path.join(plugin_dir, dir_name)

            # Check if it's a directory and if it contains a Python file with the same name
            if os.path.isdir(dir_path) and os.path.isfile(os.path.join(dir_path, dir_name + ".py")):
                # The plugin file should be in the directory and have the same name
                plugin_file = os.path.join(dir_path, dir_name + ".py")
                spec = importlib.util.spec_from_file_location(
                    dir_name, plugin_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find the plugin class
                plugin_class = None
                for attr_name in dir(module):
                    attr_value = getattr(module, attr_name)
                    if isinstance(attr_value, type) and attr_value not in [Snippet, Tool] and \
                            (issubclass(attr_value, Snippet) or issubclass(attr_value, Tool)):
                        plugin_class = attr_value
                        break

                # If a plugin class was found, add it to the database or update the existing one
                if plugin_class is not None:
                    try:
                        # Try to get the plugin
                        plugin = await PluginRegistryModel.get(name=dir_name)
                    except DoesNotExist:
                        # If the plugin does not exist, create it
                        plugin = await PluginRegistryModel.create(
                            name=plugin_class.name,
                            type=plugin_class.type,
                            display_name=plugin_class.display_name,
                            description=plugin_class.description,
                            is_public=plugin_class.is_public,
                            is_active=True,
                        )
                    else:
                        # If the plugin already existed, update the display_name, description and is_active
                        plugin.display_name = plugin_class.display_name
                        plugin.description = plugin_class.description
                        plugin.is_public = plugin_class.is_public
                        plugin.is_active = True
                        await plugin.save()


async def load_presets():
    """
    Updates core presets to match presets file
    """
    with open('presets.json', 'r') as f:
        presets = json.load(f)

    preset_ids = set(preset["id"] for preset in presets)

    db_presets = await PresetModel.all()

    for db_preset in db_presets:
        # If a database preset is not in the JSON file and is not custom, delete it
        if db_preset.id not in preset_ids and not db_preset.is_custom:
            await db_preset.delete()

    for preset in presets:
        # Combine snippets and tools into a single plugins list
        preset['plugins'] = preset.get(
            'snippets', []) + preset.get('tools', [])
        try:
            existing_preset = await PresetModel.get(id=preset["id"])
        except DoesNotExist:
            await PresetModel.create(**preset)
        else:
            for key, value in preset.items():
                setattr(existing_preset, key, value)
            await existing_preset.save()


async def load_integrations():
    """
    Updates available integrations to match config file
    """
    with open('integrations.json', 'r') as f:
        integrations = json.load(f)

    integration_names = set(integration["name"]
                            for integration in integrations)

    db_integrations = await IntegrationRegistryModel.all()

    for db_integration in db_integrations:
        if db_integration.name not in integration_names:
            await db_integration.delete()

    for integration in integrations:
        try:
            existing_integration = await IntegrationRegistryModel.get(name=integration["name"])
        except DoesNotExist:
            await IntegrationRegistryModel.create(**integration)
        else:
            for key, value in integration.items():
                setattr(existing_integration, key, value)
            await existing_integration.save()
