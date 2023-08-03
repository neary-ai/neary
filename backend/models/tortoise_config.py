import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "..", "data/db.sqlite3")
db_url = f"sqlite:///{db_path}"

TORTOISE_ORM = {
    "connections": {
        "default": db_url
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        }
    },
}