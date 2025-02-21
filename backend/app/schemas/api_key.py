

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, constr
from .base import TimestampedSchema

class APIKeyBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    is_active: bool = True
    expires_at: Optional[datetime] = None

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class APIKey(APIKeyBase, TimestampedSchema):
    id: UUID
    user_id: UUID
    key_prefix: str
    last_used_at: Optional[datetime] = None

class APIKeyFull(APIKey):
    key: str  # Full API key, only returned on creation