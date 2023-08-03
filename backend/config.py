import os
from tortoise.contrib.fastapi import register_tortoise

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "data/db.sqlite3")
db_url = f"sqlite:///{db_path}"

def init_db(app):

    register_tortoise(
        app,
        db_url=db_url,
        modules={"models": ["backend.models.models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )