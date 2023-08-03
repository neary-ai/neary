import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import init_db
from backend.auth import AuthMiddleware
from backend.routers.auth_router import router as auth_router
from backend.routers.api_router import router as api_router
from backend.routers.ws_router import router as ws_router

app = FastAPI()

init_db(app)

app.include_router(auth_router, prefix="/auth")
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)

app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=os.environ.get("ALLOW_ORIGIN_REGEX", "http://localhost(:[0-9]+)?"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)