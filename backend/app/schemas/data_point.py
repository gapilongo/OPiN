

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