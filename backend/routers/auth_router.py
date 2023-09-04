import os
import jwt
from datetime import datetime, timedelta
from passlib.hash import bcrypt

from fastapi import HTTPException, Request, Form, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from backend.models import UserModel
from backend.auth import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*30

"""
Primary authentication routes
"""

@router.post("/register")
async def register(request: Request):
    """
    Since this is a single user application, we register the user if none exists
    or update the existing user if no email is set.
    """
    data = await request.json()

    user = await UserModel.first()
    if user and user.email:
        raise HTTPException(status_code=400, detail="Account already created!")

    try:
        if user:
            user.email = data['email']
            user.password_hash = bcrypt.hash(data['password'])
            await user.save()
        else:
            user = await UserModel.create(
                email=data['email'],
                password_hash=bcrypt.hash(data['password'])
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt.encode(
            {"email": user.email, "exp": datetime.utcnow() + access_token_expires},
            JWT_SECRET,
            algorithm=ALGORITHM,
        )

        response = JSONResponse(content={"message": "Registration successful!"})
        
        cookie_attrs = {
            "key": "access_token",
            "value": access_token,
            "httponly": True,
            "secure": request.url.scheme == 'https',
            "samesite": "strict",
            "max_age": round(access_token_expires.total_seconds()),
        }

        response.set_cookie(**cookie_attrs)

        return response
    except:
        raise HTTPException(status_code=400, detail="Error creating or updating user account.")
        

@router.get("/logout")
async def logout(request: Request) -> JSONResponse:
    response = JSONResponse(content={"message": "Logged out."})
    response.delete_cookie(key="access_token")
    return response


@router.post("/token")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
) -> JSONResponse:

    user = await UserModel.get_or_none(email=email)

    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password!")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"email": email, "exp": datetime.utcnow() + access_token_expires},
        JWT_SECRET,
        algorithm=ALGORITHM,
    )

    response = JSONResponse(content={"message": "Logged in successfully"})

    cookie_attrs = {
        "key": "access_token",
        "value": access_token,
        "httponly": True,
        "secure": request.url.scheme == 'https',
        "samesite": "strict",
        "max_age": round(access_token_expires.total_seconds()),
    }

    response.set_cookie(**cookie_attrs)

    return response

@router.post("/password")
async def change_password(request: Request):
    current_user = await get_current_user(request)
    data = await request.json()
    new_password = data.get('new_password')
    
    new_password_hash = bcrypt.hash(new_password)
    current_user.password_hash = new_password_hash
    await current_user.save()

    return JSONResponse(content={"message": "Password updated successfully"})