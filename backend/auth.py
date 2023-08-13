import os
import jwt

from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware

from backend.models import UserModel

JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ENABLE_AUTH = os.environ.get("ENABLE_AUTH", "false").lower() == "true"

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if token:
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        except jwt.PyJWTError:
            if ENABLE_AUTH:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    elif ENABLE_AUTH:
        user = await UserModel.first()
        if user is None or user.email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="initial_start")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = await UserModel.first()
    
    if user is None and not ENABLE_AUTH:
        user = await UserModel.create()

    return user

"""
Auth Middleware
"""

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        protected_routes = []
        if ENABLE_AUTH and (request.url.path in protected_routes or request.url.path.startswith("/api")):
            try:
                await get_current_user(request)
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"message": e.detail})

        response = await call_next(request)
        return response