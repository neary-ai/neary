import os
import json
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.contrib.fastapi import register_tortoise
import importlib.util
from backend.models import ProgramRegistryModel, Migration

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
    await apply_migrations()

    # Register ORM with FastAPI
    register_tortoise(
        app,
        db_url=db_url,
        modules={"models": ["backend.models.models"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )

    # Populate database with programs from registry
    await init_programs()


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


async def init_programs():
    """
    Adds programs to database, and updates instances if they already exist
    """
    with open(os.path.join(base_dir, "programs/registry.json"), 'r') as f:
        programs = json.load(f)

    for program in programs:
        program_model = await ProgramRegistryModel.get_or_none(class_name=program["class_name"])
        if program_model:
            for key, value in program.items():
                setattr(program_model, key, value)
            await program_model.save()
        else:
            await ProgramRegistryModel.create(**program)
