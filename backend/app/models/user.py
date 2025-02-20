from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    ENTERPRISE = "enterprise"
    USER = "user"

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    role: UserRole = UserRole.USER
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

# File: backend/app/schemas/user.py

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional
from bson import ObjectId

from app.core.config import get_settings
from app.models.user import UserCreate, UserInDB
from app.core.security import get_password_hash

settings = get_settings()

class UserSchema:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.collection = db.users

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        user_dict = await self.collection.find_one({"email": email})
        if user_dict:
            return UserInDB(**user_dict)
        return None

    async def create(self, user: UserCreate) -> UserInDB:
        """Create new user"""
        user_dict = user.model_dump()
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = user_dict["created_at"]
        
        result = await self.collection.insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        
        return UserInDB(**user_dict)

    async def update(self, user_id: str, update_data: dict) -> Optional[UserInDB]:
        """Update user"""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["id"] = str(result.pop("_id"))
            return UserInDB(**result)
        return None

    async def delete(self, user_id: str) -> bool:
        """Delete user"""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0