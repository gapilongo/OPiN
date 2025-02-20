from typing import Optional, Dict, List, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

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
    timestamp: datetime

class DataSource(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    type: str
    version: Optional[str] = None
    metadata: Optional[Dict] = None

class DataPoint(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    category: DataCategory
    value: Union[float, str, Dict, List]
    timestamp: datetime
    source: DataSource
    quality: DataQuality = DataQuality.UNVERIFIED
    privacy_level: DataPrivacyLevel = DataPrivacyLevel.PROTECTED
    location: Optional[Location] = None
    metadata: Optional[Dict] = None
    proof: Optional[str] = None

class DataBatch(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    data_points: List[DataPoint]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
    verification_status: str = "pending"
    metadata: Optional[Dict] = None

class DataQuery(BaseModel):
    category: Optional[DataCategory] = None
    start_time: datetime
    end_time: datetime
    location_bounds: Optional[Dict] = None
    quality_threshold: Optional[DataQuality] = None
    privacy_level: Optional[DataPrivacyLevel] = None
    aggregation: Optional[str] = None
    filters: Optional[Dict] = None

class DataSubscription(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    query: DataQuery
    active: bool = True
    notification_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_notification: Optional[datetime] = None
    metadata: Optional[Dict] = None

# File: backend/app/schemas/data.py

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID

from app.models.data import DataPoint, DataBatch, DataQuery, DataSubscription

class DataSchema:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.data_points = db.data_points
        self.data_batches = db.data_batches
        self.subscriptions = db.subscriptions

    async def create_data_point(self, data_point: DataPoint) -> DataPoint:
        """Create new data point"""
        data_dict = data_point.model_dump()
        result = await self.data_points.insert_one(data_dict)
        data_dict["id"] = result.inserted_id
        return DataPoint(**data_dict)

    async def create_batch(self, batch: DataBatch) -> DataBatch:
        """Create new data batch"""
        batch_dict = batch.model_dump()
        result = await self.data_batches.insert_one(batch_dict)
        batch_dict["id"] = result.inserted_id
        return DataBatch(**batch_dict)

    async def get_data_points(self, query: DataQuery) -> List[DataPoint]:
        """Get data points based on query"""
        filter_dict = {
            "timestamp": {
                "$gte": query.start_time,
                "$lte": query.end_time
            }
        }

        if query.category:
            filter_dict["category"] = query.category

        if query.quality_threshold:
            filter_dict["quality"] = {"$gte": query.quality_threshold}

        if query.location_bounds:
            filter_dict["location"] = {
                "$geoWithin": {
                    "$box": query.location_bounds
                }
            }

        cursor = self.data_points.find(filter_dict)
        return [DataPoint(**doc) for doc in await cursor.to_list(length=None)]

    async def update_data_point(self, data_point_id: UUID, updates: Dict) -> Optional[DataPoint]:
        """Update data point"""
        result = await self.data_points.find_one_and_update(
            {"id": data_point_id},
            {"$set": updates},
            return_document=True
        )
        if result:
            return DataPoint(**result)
        return None

    async def create_subscription(self, subscription: DataSubscription) -> DataSubscription:
        """Create new data subscription"""
        sub_dict = subscription.model_dump()
        result = await self.subscriptions.insert_one(sub_dict)
        sub_dict["id"] = result.inserted_id
        return DataSubscription(**sub_dict)

    async def get_active_subscriptions(self) -> List[DataSubscription]:
        """Get all active subscriptions"""
        cursor = self.subscriptions.find({"active": True})
        return [DataSubscription(**doc) for doc in await cursor.to_list(length=None)]

    async def update_subscription(self, subscription_id: UUID, updates: Dict) -> Optional[DataSubscription]:
        """Update subscription"""
        result = await self.subscriptions.find_one_and_update(
            {"id": subscription_id},
            {"$set": updates},
            return_document=True
        )
        if result:
            return DataSubscription(**result)
        return None