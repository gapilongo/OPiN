from typing import Dict, Any, Optional
import hashlib
import json
from datetime import datetime
from abc import ABC, abstractmethod

from app.models.data import DataPoint, DataCategory, DataPrivacyLevel
from app.core.config import get_settings

settings = get_settings()

class ZKPCircuit(ABC):
    """Abstract base class for ZKP circuits"""
    
    @abstractmethod
    async def generate_proof(self, private_inputs: Dict[str, Any], public_inputs: Dict[str, Any]) -> str:
        pass
        
    @abstractmethod
    async def verify_proof(self, proof: str, public_inputs: Dict[str, Any]) -> bool:
        pass

class LocationCircuit(ZKPCircuit):
    """ZKP circuit for location data"""
    
    async def generate_proof(self, private_inputs: Dict[str, Any], public_inputs: Dict[str, Any]) -> str:
        """
        Generate ZKP proof for location data
        In production, this would use actual ZK-SNARK implementation
        """
        # Simulate proof generation
        proof_data = {
            "type": "location",
            "region_hash": self._hash_region(
                private_inputs["latitude"],
                private_inputs["longitude"],
                public_inputs["accuracy"]
            ),
            "timestamp": datetime.utcnow().isoformat()
        }
        return self._generate_mock_proof(proof_data)
        
    async def verify_proof(self, proof: str, public_inputs: Dict[str, Any]) -> bool:
        """Verify location proof"""
        try:
            # In production, this would use actual ZK-SNARK verification
            proof_data = json.loads(proof)
            return (
                proof_data["type"] == "location" and
                "region_hash" in proof_data and
                "timestamp" in proof_data
            )
        except:
            return False
            
    def _hash_region(self, lat: float, lng: float, accuracy: float) -> str:
        """Create hash of geographic region"""
        region = f"{round(lat/accuracy)},{round(lng/accuracy)}"
        return hashlib.sha256(region.encode()).hexdigest()
        
    def _generate_mock_proof(self, data: Dict) -> str:
        """Generate mock proof"""
        return json.dumps(data)

class BehavioralCircuit(ZKPCircuit):
    """ZKP circuit for behavioral data"""
    
    async def generate_proof(self, private_inputs: Dict[str, Any], public_inputs: Dict[str, Any]) -> str:
        """Generate ZKP proof for behavioral data"""
        # Remove sensitive information but preserve patterns
        proof_data = {
            "type": "behavioral",
            "pattern_hash": self._hash_pattern(private_inputs),
            "category": public_inputs.get("category", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
        return self._generate_mock_proof(proof_data)
        
    async def verify_proof(self, proof: str, public_inputs: Dict[str, Any]) -> bool:
        """Verify behavioral proof"""
        try:
            proof_data = json.loads(proof)
            return (
                proof_data["type"] == "behavioral" and
                "pattern_hash" in proof_data and
                "category" in proof_data
            )
        except:
            return False
            
    def _hash_pattern(self, data: Dict) -> str:
        """Hash behavioral pattern while preserving privacy"""
        pattern = {
            k: v for k, v in data.items()
            if k not in {"user_id", "device_id", "ip_address"}
        }
        return hashlib.sha256(json.dumps(pattern).encode()).hexdigest()
        
    def _generate_mock_proof(self, data: Dict) -> str:
        """Generate mock proof"""
        return json.dumps(data)

class ZKPService:
    """Main service for handling zero-knowledge proofs"""
    
    def __init__(self):
        self.circuits = {
            DataCategory.SENSOR: LocationCircuit(),
            DataCategory.BEHAVIORAL: BehavioralCircuit()
        }
    
    async def generate_proof(self, data_point: DataPoint) -> Optional[str]:
        """Generate ZKP proof for a data point"""
        circuit = self.circuits.get(data_point.category)
        if not circuit:
            return None
            
        # Separate private and public inputs
        private_inputs, public_inputs = self._prepare_inputs(data_point)
        
        # Generate proof
        return await circuit.generate_proof(private_inputs, public_inputs)
    
    async def verify_proof(self, data_point: DataPoint) -> bool:
        """Verify ZKP proof"""
        if not data_point.proof:
            return False
            
        circuit = self.circuits.get(data_point.category)
        if not circuit:
            return False
            
        # Extract public inputs
        _, public_inputs = self._prepare_inputs(data_point)
        
        # Verify proof
        return await circuit.verify_proof(data_point.proof, public_inputs)
    
    def _prepare_inputs(self, data_point: DataPoint) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare private and public inputs for proof generation"""
        if data_point.category == DataCategory.SENSOR:
            return self._prepare_sensor_inputs(data_point)
        elif data_point.category == DataCategory.BEHAVIORAL:
            return self._prepare_behavioral_inputs(data_point)
        else:
            return {}, {}
    
    def _prepare_sensor_inputs(self, data_point: DataPoint) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare inputs for sensor data"""
        private_inputs = {
            "latitude": data_point.location.latitude if data_point.location else 0,
            "longitude": data_point.location.longitude if data_point.location else 0,
            "value": data_point.value
        }
        
        public_inputs = {
            "accuracy": data_point.location.accuracy if data_point.location else 1000,
            "timestamp": data_point.timestamp.isoformat()
        }
        
        return private_inputs, public_inputs
    
    def _prepare_behavioral_inputs(self, data_point: DataPoint) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare inputs for behavioral data"""
        private_inputs = data_point.value if isinstance(data_point.value, dict) else {}
        
        public_inputs = {
            "category": data_point.category.value,
            "timestamp": data_point.timestamp.isoformat()
        }
        
        return private_inputs, public_inputs