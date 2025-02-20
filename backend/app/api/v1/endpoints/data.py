from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime

from app.core.security import get_current_user
from app.api.deps import get_db
from app.models.data import (
    DataPoint,
    DataBatch,
    DataQuery,
    DataSubscription
)
from app.schemas.data import DataSchema
from app.services.data_processing import BatchProcessor, DataAggregator
from app.services.zkp import ZKPService

router = APIRouter()
batch_processor = BatchProcessor()
data_aggregator = DataAggregator()
zkp_service = ZKPService()

@router.post("/submit", response_model=DataPoint)
async def submit_data(
    data_point: DataPoint,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Submit a single data point"""
    try:
        # Process data point
        processed_point = await batch_processor._process_point(data_point)
        
        # Store in database
        data_schema = DataSchema(db)
        stored_point = await data_schema.create_data_point(processed_point)
        
        return stored_point
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/submit/batch", response_model=DataBatch)
async def submit_batch(
    batch: DataBatch,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Submit a batch of data points"""
    try:
        # Process batch
        processed_batch = await batch_processor.process_batch(batch)
        
        # Store in database
        data_schema = DataSchema(db)
        stored_batch = await data_schema.create_batch(processed_batch)
        
        return stored_batch
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/query", response_model=List[DataPoint])
async def query_data(
    query: DataQuery,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Query data points"""
    try:
        data_schema = DataSchema(db)
        results = await data_schema.get_data_points(query)
        
        # Apply aggregation if requested
        if query.aggregation:
            aggregated = await data_aggregator.aggregate(
                results,
                query.aggregation
            )
            return aggregated
            
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/subscribe", response_model=DataSubscription)
async def create_subscription(
    subscription: DataSubscription,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create new data subscription"""
    try:
        data_schema = DataSchema(db)
        subscription.user_id = current_user
        created_sub = await data_schema.create_subscription(subscription)
        return created_sub
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/verify/{data_point_id}")
async def verify_data_point(
    data_point_id: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Verify a data point's proof"""
    try:
        data_schema = DataSchema(db)
        data_point = await data_schema.get_data_point(data_point_id)
        
        if not data_point:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data point not found"
            )
            
        is_valid = await zkp_service.verify_proof(data_point)
        
        return {
            "valid": is_valid,
            "verification_time": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )