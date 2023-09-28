import os
import jwt

from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import SessionLocal
from backend.services import user_service

ENABLE_AUTH = settings.application.get("ENABLE_AUTH", False)
JWT_SECRET = settings.application.get("JWT_SECRET", "your-secret-key")
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*30
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if token:
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        except jwt.PyJWTError:
            if ENABLE_AUTH:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    elif ENABLE_AUTH:
        user = user_service.get_user_by_id(db, 1)
        if user is None or user.email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="initial_start")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = user_service.get_user_by_id(db, 1)
    
    if user is None and not ENABLE_AUTH:
        user_data = {}
        user = user_service.create_user(db, user_data)

    return user

"""
Auth Middleware
"""

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        protected_routes = []
        unprotected_routes = ["/api/oauth2/callback"]

        if ENABLE_AUTH and (request.url.path in protected_routes or (request.url.path.startswith("/api") and request.url.path not in unprotected_routes)):
            db = SessionLocal()
            try:
                get_current_user(request, db)
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"message": e.detail})
            finally:
                db.close()

        response = await call_next(request)
        return response