

from typing import Dict, Optional, Any
from uuid import UUID
from pydantic import BaseModel, HttpUrl
from .base import TimestampedSchema
from .data_point import DataCategory

class SubscriptionBase(BaseModel):
    category: DataCategory
    filters: Optional[Dict[str, Any]] = None
    notification_url: Optional[HttpUrl] = None
    is_active: bool = True

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    category: Optional[DataCategory] = None
    filters: Optional[Dict[str, Any]] = None
    notification_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None

class Subscription(SubscriptionBase, TimestampedSchema):
    id: UUID
    user_id: UUID