from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import timedelta
from typing import Any

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    verify_password,
    Token
)
from app.models.user import User, UserCreate
from app.schemas.user import UserSchema
from app.api.deps import get_db

settings = get_settings()
router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    db: AsyncIOMotorClient = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user_schema = UserSchema(db)
    user = await user_schema.get_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=User)
async def register(
    *,
    db: AsyncIOMotorClient = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """
    Register new user
    """
    user_schema = UserSchema(db)
    user = await user_schema.get_by_email(user_in.email)
    
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await user_schema.create(user_in)
    return user

# File: backend/app/api/deps.py

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Generator
from app.core.config import get_settings

settings = get_settings()

async def get_db() -> Generator:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    try:
        yield client
    finally:
        client.close()