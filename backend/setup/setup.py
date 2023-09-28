import os
import re
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from alembic.config import Config
from alembic import command

from backend.config import settings
from backend.models import PresetModel, IntegrationRegistryModel
from backend.services import PluginManager

def run_setup(db_url: str):
    try:
        # Create an engine that knows how to connect to the database
        engine = create_engine(db_url)

        #Create the database if it doesn't exist
        if not database_exists(engine.url):
            create_database(engine.url)

        # Create a new Sessionmaker bound to the engine
        SessionLocal = sessionmaker(bind=engine)

        # Create a Alembic configuration object
        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))

        # Set the SQLAlchemy URL to the one used for testing
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        # Upgrade to the latest version
        command.upgrade(alembic_cfg, "head")

        load_presets(SessionLocal)
        load_integrations(SessionLocal)
        PluginManager(SessionLocal).load_plugins()
    except Exception as e:
        print(f"An error occurred: {e}")


def load_presets(SessionLocal):
    """
    Updates core presets
    """
    # Create a new session
    session = SessionLocal()

    with open(os.path.join(current_dir, "presets.json"), 'r') as f:
        presets = json.load(f)

    for preset in presets:
        existing_preset = session.query(
            PresetModel).filter_by(name=preset["name"]).first()
        if existing_preset is None:
            new_preset = PresetModel(**preset)
            session.add(new_preset)
        else:
            if not existing_preset.is_custom:
                for key, value in preset.items():
                    setattr(existing_preset, key, value)

    # Commit the changes
    session.commit()


def load_integrations(SessionLocal):
    """
    Updates available integrations to match config file
    """
    # Create a new session
    session = SessionLocal()

    with open(os.path.join(current_dir, "integrations.json"), 'r') as f:
        integrations = json.load(f)

    # Replace placeholders with values from settings.toml
    for integration in integrations:
        for key, value in integration["data"].items():
            if isinstance(value, str):
                integration["data"][key] = re.sub(
                    r'\{(.+?)\}', lambda m: settings.get(m.group(1), m.group(0)), value)

    integration_names = set(integration["name"]
                            for integration in integrations)

    db_integrations = session.query(IntegrationRegistryModel).all()

    for db_integration in db_integrations:
        if db_integration.name not in integration_names:
            session.delete(db_integration)

    for integration in integrations:
        existing_integration = session.query(
            IntegrationRegistryModel).filter_by(name=integration["name"]).first()
        if existing_integration is None:
            new_integration = IntegrationRegistryModel(**integration)
            session.add(new_integration)
        else:
            for key, value in integration.items():
                setattr(existing_integration, key, value)

    # Commit the changes
    session.commit()
