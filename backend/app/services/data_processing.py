from typing import List, Dict, Optional, Any
import asyncio
from datetime import datetime
import json
from abc import ABC, abstractmethod

from app.models.data import (
    DataPoint,
    DataBatch,
    DataCategory,
    DataQuality,
    DataPrivacyLevel
)
from app.services.zkp import ZKPService
from app.core.config import get_settings

settings = get_settings()

class DataProcessor(ABC):
    """Abstract base class for data processors"""
    
    @abstractmethod
    async def process(self, data: DataPoint) -> DataPoint:
        """Process a single data point"""
        pass

    @abstractmethod
    async def validate(self, data: DataPoint) -> bool:
        """Validate data point"""
        pass

class SensorDataProcessor(DataProcessor):
    """Processor for sensor data"""
    
    async def process(self, data: DataPoint) -> DataPoint:
        """Process sensor data"""
        if not await self.validate(data):
            data.quality = DataQuality.LOW
            return data

        # Apply sensor-specific processing
        if isinstance(data.value, (int, float)):
            # Apply statistical outlier detection
            if await self._is_outlier(data.value):
                data.quality = DataQuality.LOW
            else:
                data.quality = DataQuality.HIGH
        
        # Add proof of processing
        data.metadata = data.metadata or {}
        data.metadata["processed_at"] = datetime.utcnow().isoformat()
        
        return data

    async def validate(self, data: DataPoint) -> bool:
        """Validate sensor data"""
        if data.category != DataCategory.SENSOR:
            return False
            
        if not isinstance(data.value, (int, float, dict)):
            return False
            
        if data.location and not self._validate_location(data.location):
            return False
            
        return True

    async def _is_outlier(self, value: float, threshold: float = 3.0) -> bool:
        """Simple outlier detection"""
        # In production, this would use more sophisticated methods
        # and historical data for comparison
        return abs(value) > threshold

    def _validate_location(self, location: Dict) -> bool:
        """Validate location data"""
        required_fields = {"latitude", "longitude", "timestamp"}
        return all(field in location for field in required_fields)

class BehavioralDataProcessor(DataProcessor):
    """Processor for behavioral data"""
    
    async def process(self, data: DataPoint) -> DataPoint:
        """Process behavioral data"""
        if not await self.validate(data):
            data.quality = DataQuality.LOW
            return data

        # Anonymize sensitive information
        data = await self._anonymize_data(data)
        
        # Verify data consistency
        if await self._verify_consistency(data):
            data.quality = DataQuality.HIGH
        else:
            data.quality = DataQuality.MEDIUM

        return data

    async def validate(self, data: DataPoint) -> bool:
        """Validate behavioral data"""
        if data.category != DataCategory.BEHAVIORAL:
            return False
            
        if not isinstance(data.value, dict):
            return False
            
        required_fields = {"action", "context", "timestamp"}
        return all(field in data.value for field in required_fields)

    async def _anonymize_data(self, data: DataPoint) -> DataPoint:
        """Anonymize sensitive information"""
        if isinstance(data.value, dict):
            # Remove direct identifiers
            sensitive_fields = {"user_id", "device_id", "ip_address"}
            data.value = {
                k: v for k, v in data.value.items()
                if k not in sensitive_fields
            }
            
        return data

    async def _verify_consistency(self, data: DataPoint) -> bool:
        """Verify data consistency"""
        if not isinstance(data.value, dict):
            return False
            
        # Check timestamp consistency
        event_time = datetime.fromisoformat(data.value["timestamp"])
        if abs((event_time - data.timestamp).total_seconds()) > 300:  # 5 minutes
            return False
            
        return True

class BatchProcessor:
    """Process batches of data points"""
    
    def __init__(self):
        self.processors = {
            DataCategory.SENSOR: SensorDataProcessor(),
            DataCategory.BEHAVIORAL: BehavioralDataProcessor()
        }
        self.zkp_service = ZKPService()

    async def process_batch(self, batch: DataBatch) -> DataBatch:
        """Process a batch of data points"""
        processed_points = []
        
        # Process data points in parallel
        tasks = [
            self._process_point(point)
            for point in batch.data_points
        ]
        processed_points = await asyncio.gather(*tasks)
        
        batch.data_points = processed_points
        batch.processed = True
        batch.verification_status = "completed"
        
        return batch

    async def _process_point(self, point: DataPoint) -> DataPoint:
        """Process a single data point"""
        processor = self.processors.get(point.category)
        if not processor:
            point.quality = DataQuality.LOW
            return point

        # Process data
        processed_point = await processor.process(point)
        
        # Generate ZKP proof if needed
        if processed_point.privacy_level in {DataPrivacyLevel.PRIVATE, DataPrivacyLevel.SENSITIVE}:
            proof = await self.zkp_service.generate_proof(processed_point)
            processed_point.proof = proof

        return processed_point

class DataAggregator:
    """Aggregate processed data"""
    
    async def aggregate(self, data_points: List[DataPoint], aggregation_type: str) -> Dict[str, Any]:
        """Aggregate data points"""
        if not data_points:
            return {}

        if aggregation_type == "sum":
            return await self._aggregate_sum(data_points)
        elif aggregation_type == "average":
            return await self._aggregate_average(data_points)
        elif aggregation_type == "statistics":
            return await self._aggregate_statistics(data_points)
        else:
            raise ValueError(f"Unsupported aggregation type: {aggregation_type}")

    async def _aggregate_sum(self, data_points: List[DataPoint]) -> Dict[str, float]:
        """Calculate sum of numeric values"""
        total = 0.0
        for point in data_points:
            if isinstance(point.value, (int, float)):
                total += float(point.value)
        return {"sum": total}

    async def _aggregate_average(self, data_points: List[DataPoint]) -> Dict[str, float]:
        """Calculate average of numeric values"""
        values = [
            float(point.value)
            for point in data_points
            if isinstance(point.value, (int, float))
        ]
        if not values:
            return {"average": 0.0}
        return {"average": sum(values) / len(values)}

    async def _aggregate_statistics(self, data_points: List[DataPoint]) -> Dict[str, Any]:
        """Calculate basic statistics"""
        values = [
            float(point.value)
            for point in data_points
            if isinstance(point.value, (int, float))
        ]
        if not values:
            return {}
            
        sorted_values = sorted(values)
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "average": sum(values) / len(values),
            "median": sorted_values[len(sorted_values) // 2]
        }