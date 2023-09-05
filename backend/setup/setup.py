import os
import re
import json
import importlib.util

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.contrib.fastapi import register_tortoise

from backend.config import settings
from backend.models import PresetModel, IntegrationRegistryModel, Migration
from backend.services import PluginManager

current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

db_path = os.path.join(base_dir, "data/db.sqlite3")
db_url = f"sqlite:///{db_path}"

async def run_setup(app):
    # Initialize ORM
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["backend.models.models"]}
    )

    # Apply migrations, if necessary
    await apply_migrations()

    # Register ORM with FastAPI
    register_tortoise(
        app,
        db_url=db_url,
        modules={"models": ["backend.models.models"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )

    await load_presets()
    await load_integrations()

    # Load PluginManager into memory as a singleton
    PluginManager()


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


async def load_presets():
    """
    Updates core presets to match presets file
    """
    with open(os.path.join(current_dir, "presets.json"), 'r') as f:
        presets = json.load(f)

    preset_ids = set(preset["id"] for preset in presets)

    db_presets = await PresetModel.all()

    for db_preset in db_presets:
        # If a database preset is not in the JSON file and is not custom, delete it
        if db_preset.id not in preset_ids and not db_preset.is_custom:
            await db_preset.delete()

    for preset in presets:
        try:
            existing_preset = await PresetModel.get(id=preset["id"])
        except DoesNotExist:
            await PresetModel.create(**preset)
        else:
            if not existing_preset.is_custom:
                for key, value in preset.items():
                    setattr(existing_preset, key, value)
                await existing_preset.save()

async def load_integrations():
    """
    Updates available integrations to match config file
    """
    with open(os.path.join(current_dir, "integrations.json"), 'r') as f:
        integrations = json.load(f)

    # Replace placeholders with values from settings.toml
    for integration in integrations:
        for key, value in integration["data"].items():
            if isinstance(value, str):
                integration["data"][key] = re.sub(r'\{(.+?)\}', lambda m: settings.get(m.group(1), m.group(0)), value)

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
