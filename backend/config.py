import os
from dynaconf import Dynaconf

base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(base_dir)

settings = Dynaconf(
    settings_files=['settings.toml'],
    load_dotenv=True,
    root_path=project_root
)