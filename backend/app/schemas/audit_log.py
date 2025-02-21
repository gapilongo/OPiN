

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