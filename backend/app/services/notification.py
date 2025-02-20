from fastapi import APIRouter, Depends, HTTPException, status, Header
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.core.security import get_current_user
from app.api.deps import get_db
from app.models.data import (
    DataCategory,
    DataQuery,
    DataSubscription,
    DataPoint
)
from app.schemas.data import DataSchema
from app.services.data_processing import DataAggregator
from app.core.config import get_settings

settings = get_settings()
router = APIRouter()
data_aggregator = DataAggregator()

class EnterprisePermissions:
    """Handle enterprise permissions and rate limiting"""
    
    def __init__(self):
        self.rate_limits = {
            "basic": 1000,      # requests per day
            "premium": 10000,
            "enterprise": 100000
        }
        self.cache = {}  # In production, use Redis
        
    async def check_rate_limit(self, api_key: str) -> bool:
        """Check if request is within rate limit"""
        if api_key not in self.cache:
            self.cache[api_key] = {
                "count": 0,
                "reset_time": datetime.utcnow() + timedelta(days=1)
            }
            
        cache_data = self.cache[api_key]
        if datetime.utcnow() > cache_data["reset_time"]:
            cache_data["count"] = 0
            cache_data["reset_time"] = datetime.utcnow() + timedelta(days=1)
            
        tier = await self.get_enterprise_tier(api_key)
        if cache_data["count"] >= self.rate_limits[tier]:
            return False
            
        cache_data["count"] += 1
        return True
        
    async def get_enterprise_tier(self, api_key: str) -> str:
        """Get enterprise tier from API key"""
        # In production, fetch from database
        return "basic"

permissions = EnterprisePermissions()

@router.post("/data/query", response_model=Dict[str, Any])
async def enterprise_query(
    query: DataQuery,
    db: AsyncIOMotorClient = Depends(get_db),
    api_key: str = Header(...),
    current_user: str = Depends(get_current_user)
):
    """Enterprise data query endpoint with analytics"""
    if not await permissions.check_rate_limit(api_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
        
    try:
        data_schema = DataSchema(db)
        results = await data_schema.get_data_points(query)
        
        # Process results for enterprise consumption
        processed_results = await process_enterprise_data(results, query)
        
        return {
            "data": processed_results,
            "metadata": {
                "query_time": datetime.utcnow(),
                "result_count": len(results),
                "query_params": query.model_dump()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/subscription/create", response_model=DataSubscription)
async def create_enterprise_subscription(
    subscription: DataSubscription,
    db: AsyncIOMotorClient = Depends(get_db),
    api_key: str = Header(...),
    current_user: str = Depends(get_current_user)
):
    """Create enterprise data subscription"""
    try:
        # Validate enterprise permissions
        tier = await permissions.get_enterprise_tier(api_key)
        if tier not in ["premium", "enterprise"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Subscription requires premium or enterprise tier"
            )
            
        data_schema = DataSchema(db)
        subscription.user_id = current_user
        subscription.metadata = subscription.metadata or {}
        subscription.metadata["enterprise_tier"] = tier
        
        created_sub = await data_schema.create_subscription(subscription)
        return created_sub
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/analytics/overview")
async def get_analytics_overview(
    db: AsyncIOMotorClient = Depends(get_db),
    api_key: str = Header(...),
    current_user: str = Depends(get_current_user)
):
    """Get overview analytics for enterprise dashboard"""
    try:
        # Get recent data points
        data_schema = DataSchema(db)
        recent_query = DataQuery(
            start_time=datetime.utcnow() - timedelta(days=30),
            end_time=datetime.utcnow()
        )
        recent_data = await data_schema.get_data_points(recent_query)
        
        # Calculate analytics
        analytics = await calculate_enterprise_analytics(recent_data)
        
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def process_enterprise_data(
    data_points: List[DataPoint],
    query: DataQuery
) -> List[Dict[str, Any]]:
    """Process data points for enterprise consumption"""
    processed_data = []
    
    for point in data_points:
        processed_point = {
            "id": str(point.id),
            "timestamp": point.timestamp,
            "category": point.category,
            "value": point.value,
            "quality": point.quality,
            "metadata": point.metadata
        }
        
        # Add aggregated metrics if requested
        if query.aggregation:
            aggregated = await data_aggregator.aggregate(
                [point],
                query.aggregation
            )
            processed_point["aggregated"] = aggregated
            
        processed_data.append(processed_point)
        
    return processed_data

async def calculate_enterprise_analytics(
    data_points: List[DataPoint]
) -> Dict[str, Any]:
    """Calculate enterprise analytics"""
    analytics = {
        "total_points": len(data_points),
        "categories": {},
        "quality_distribution": {
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "temporal_distribution": {}
    }
    
    # Calculate distributions
    for point in data_points:
        # Category distribution
        category = point.category.value
        analytics["categories"][category] = analytics["categories"].get(category, 0) + 1
        
        # Quality distribution
        quality = point.quality.value.lower()
        analytics["quality_distribution"][quality] += 1
        
        # Temporal distribution (by day)
        day = point.timestamp.date().isoformat()
        analytics["temporal_distribution"][day] = (
            analytics["temporal_distribution"].get(day, 0) + 1
        )
    
    # Calculate percentages
    total = len(data_points)
    if total > 0:
        for category in analytics["categories"]:
            analytics["categories"][category] = (
                analytics["categories"][category] / total * 100
            )
        
        for quality in analytics["quality_distribution"]:
            analytics["quality_distribution"][quality] = (
                analytics["quality_distribution"][quality] / total * 100
            )
    
    return analytics