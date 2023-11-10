import uvicorn
import os
import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
sys.path.append(str(Path(__file__).parent.parent))

from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from routes import routes
from core.setup import run_setup
from auth.middleware import AuthMiddleware
from database import SQLALCHEMY_DATABASE_URL

app = FastAPI()

for route, prefix in routes:
    app.include_router(route, prefix=prefix)


@app.on_event("startup")
async def app_startup():
    run_setup(SQLALCHEMY_DATABASE_URL)


# Serve our static files from the frontend
@app.get("/{catch_all:path}", response_class=HTMLResponse)
async def catch_all(catch_all: str):
    path = os.path.join(str(current_dir / ".." / "frontend" / "dist"), catch_all)
    if os.path.isfile(path):
        return FileResponse(path)
    else:
        with open(
            os.path.join(str(current_dir / ".." / "frontend" / "dist"), "index.html"),
            "r",
        ) as f:
            content = f.read()
        return HTMLResponse(content=content)


app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=os.environ.get(
        "ALLOW_ORIGIN_REGEX", "http://localhost(:[0-9]+)?"
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    dev_env = os.environ.get("DEV_ENV", False) == "true"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=dev_env)
