import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from alembic.config import Config
from alembic import command

from modules.plugins.services.plugin_loader import PluginLoader
from modules.presets.services.preset_service import PresetService
from modules.integrations.services.integration_service import IntegrationService

current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_setup(db_url: str):
    try:
        engine = create_engine(db_url)

        if not database_exists(engine.url):
            create_database(engine.url)

        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))

        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        # Apply all migrations
        command.upgrade(alembic_cfg, "head")

        # Create database session
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        # Seed database
        PresetService(session).load_presets()
        IntegrationService(session).load_integrations()
        PluginLoader(session).load_plugins()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()
