from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings
from database import SessionLocal
from users.services import UserService

ENABLE_AUTH = settings.application.get("ENABLE_AUTH", False)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        protected_routes = []
        unprotected_routes = ["/api/oauth2/callback"]

        if ENABLE_AUTH and (
            request.url.path in protected_routes
            or (
                request.url.path.startswith("/api")
                and request.url.path not in unprotected_routes
            )
        ):
            db = SessionLocal()
            try:
                user_service = UserService(db)
                user_service.get_current_user(request)
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code, content={"message": e.detail}
                )
            finally:
                db.close()

        response = await call_next(request)
        return response
