import os
import jwt

from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware
from tortoise.exceptions import DoesNotExist

from backend.models import UserModel

"""
Authentication helpers
"""

JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user = await UserModel.get_or_none(email=payload["email"])
        return user
    except (jwt.PyJWTError, DoesNotExist):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

"""
Auth Middleware
"""
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        protected_routes = []
        if request.url.path in protected_routes or request.url.path.startswith("/api"):
            try:
                await get_current_user(request)
            except HTTPException as e:
                if e.status_code == status.HTTP_401_UNAUTHORIZED:
                    user_count = await UserModel.all().count()
                    if user_count == 0:
                        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "initial_start"})
                    else:
                        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Not authenticated!"})

        response = await call_next(request)
        return response