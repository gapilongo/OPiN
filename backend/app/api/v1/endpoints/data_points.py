

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from app.schemas.data_point import (
    DataPoint,
    DataPointCreate,
    DataCategory,
    DataQuality
)
from app.schemas.responses import (
    DataResponse,
    PaginatedResponse
)
from app.services import data_service
from app.api import deps

router = APIRouter()

@router.post(
    "/",
    response_model=DataResponse[DataPoint],
    status_code=201,
    responses={
        201: {
            "description": "Data point created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "category": "SENSOR",
                            "value": {
                                "temperature": 25.5,
                                "humidity": 60
                            },
                            "quality": "HIGH",
                            "created_at": "2024-02-21T10:00:00Z"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid data format",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": "Invalid data format",
                        "details": [
                            {
                                "loc": ["body", "value"],
                                "msg": "Invalid value format",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def create_data_point(
    data_in: DataPointCreate,
    current_user = Depends(deps.get_current_user),
    db = Depends(deps.get_db)
):
    """
    Create a new data point.
    
    The data point will be validated and processed according to its category.
    If subscriptions match the data point's criteria, notifications will be sent.
    
    - **category**: Type of data (SENSOR, BEHAVIORAL, etc.)
    - **value**: Actual data value (format depends on category)
    - **quality**: Optional quality indicator (defaults to UNVERIFIED)
    - **privacy_level**: Optional privacy level (defaults to PROTECTED)
    - **location**: Optional location information
    - **metadata**: Optional additional information
    """
    result = await data_service.create_data_point(
        db=db,
        obj_in=data_in,
        creator_id=current_user.id
    )
    return DataResponse(success=True, data=result)

@router.get(
    "/",
    response_model=PaginatedResponse[DataPoint],
    responses={
        200: {
            "description": "List of data points",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "total": 100,
                        "page": 1,
                        "page_size": 10,
                        "items": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "category": "SENSOR",
                                "value": {
                                    "temperature": 25.5,
                                    "humidity": 60
                                },
                                "quality": "HIGH",
                                "created_at": "2024-02-21T10:00:00Z"
                            }
                        ]
                    }
                }
            }
        }
    }
)