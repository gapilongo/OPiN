

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class TimestampedSchema(BaseSchema):
    created_at: datetime
    updated_at: Optional[datetime] = None

# File: backend/app/schemas/data_point.py

from typing import Any, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field
from .base import TimestampedSchema

class DataCategory(str, Enum):
    SENSOR = "sensor"
    BEHAVIORAL = "behavioral"
    ENVIRONMENTAL = "environmental"
    MARKET = "market"
    AI_TRAINING = "ai_training"

class DataQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"

class DataPrivacyLevel(str, Enum):
    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"
    SENSITIVE = "sensitive"

class Location(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = Field(None, ge=0)
    altitude: Optional[float] = None

class DataPointBase(BaseModel):
    category: DataCategory
    value: Any
    quality: DataQuality = DataQuality.UNVERIFIED
    privacy_level: DataPrivacyLevel = DataPrivacyLevel.PROTECTED
    location: Optional[Location] = None
    metadata: Optional[Dict[str, Any]] = None

class DataPointCreate(DataPointBase):
    pass

class DataPointUpdate(BaseModel):
    category: Optional[DataCategory] = None
    value: Optional[Any] = None
    quality: Optional[DataQuality] = None
    privacy_level: Optional[DataPrivacyLevel] = None
    location: Optional[Location] = None
    metadata: Optional[Dict[str, Any]] = None

class DataPoint(DataPointBase, TimestampedSchema):
    id: UUID
    creator_id: Optional[UUID] = None

# File: backend/app/schemas/subscription.py

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

# File: backend/app/schemas/api_key.py

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

# File: backend/app/schemas/audit_log.py

from typing import Dict, Optional, Any
from uuid import UUID
from pydantic import BaseModel
from .base import TimestampedSchema

class AuditLogBase(BaseModel):
    action: str
    entity_type: str
    entity_id: UUID
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    user_id: UUID

class AuditLog(AuditLogBase, TimestampedSchema):
    id: UUID

# File: backend/app/schemas/responses.py

from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel

DataT = TypeVar('DataT')

class ResponseBase(BaseModel):
    success: bool
    message: Optional[str] = None

class DataResponse(ResponseBase, Generic[DataT]):
    data: Optional[DataT] = None

class PaginatedResponse(DataResponse, Generic[DataT]):
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    items: List[DataT]

class ErrorDetail(BaseModel):
    loc: List[str]
    msg: str
    type: str

class ErrorResponse(ResponseBase):
    error: Optional[str] = None
    details: Optional[List[ErrorDetail]] = None
    debug_info: Optional[Dict[str, Any]] = None

# File: backend/app/schemas/__init__.py

from .base import BaseSchema, TimestampedSchema
from .user import User, UserCreate, UserUpdate, UserInDB
from .data_point import (
    DataPoint, DataPointCreate, DataPointUpdate,
    DataCategory, DataQuality, DataPrivacyLevel, Location
)
from .subscription import Subscription, SubscriptionCreate, SubscriptionUpdate
from .api_key import APIKey, APIKeyCreate, APIKeyUpdate, APIKeyFull
from .audit_log import AuditLog, AuditLogCreate
from .responses import (
    ResponseBase, DataResponse, PaginatedResponse,
    ErrorResponse, ErrorDetail
)

__all__ = [
    "BaseSchema",
    "TimestampedSchema",
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "DataPoint",
    "DataPointCreate",
    "DataPointUpdate",
    "DataCategory",
    "DataQuality",
    "DataPrivacyLevel",
    "Location",
    "Subscription",
    "SubscriptionCreate",
    "SubscriptionUpdate",
    "APIKey",
    "APIKeyCreate",
    "APIKeyUpdate",
    "APIKeyFull",
    "AuditLog",
    "AuditLogCreate",
    "ResponseBase",
    "DataResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "ErrorDetail"
]