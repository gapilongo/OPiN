import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Request logging
        request_id = request.headers.get("X-Request-ID", "")
        logger.info(f"Request {request_id}: {request.method} {request.url}")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Response logging
            process_time = time.time() - start_time
            logger.info(
                f"Request {request_id} completed: {response.status_code} "
                f"({process_time:.2f}s)"
            )
            
            return response
        except Exception as e:
            logger.error(f"Request {request_id} failed: {str(e)}")
            raise

# File: backend/app/middleware/rate_limiter.py

from fastapi import Request, Response, HTTPException
import time
from collections import defaultdict
import asyncio
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        
    async def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.requests[key]) >= self.requests_per_minute:
            return False
            
        # Add new request
        self.requests[key].append(now)
        return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute)
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client identifier (IP or API key)
        client_id = request.headers.get("X-API-Key", request.client.host)
        
        if not await self.limiter.check_rate_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
            
        return await call_next(request)

# File: backend/app/middleware/error_handler.py

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from typing import Union
import traceback

async def http_error_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error"
            }
        }
    )

async def generic_error_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle generic exceptions"""
    # Log the full traceback
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "server_error"
            }
        }
    )

# File: backend/app/utils/validation.py

from typing import Any, Dict, Optional
from datetime import datetime
import re
from pydantic import ValidationError

def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    if not api_key:
        return False
    
    # Check format (example: opin_xxxxx where x is alphanumeric)
    pattern = r'^opin_[a-zA-Z0-9]{32}$'
    return bool(re.match(pattern, api_key))

def validate_timestamp(timestamp: Union[str, datetime]) -> Optional[datetime]:
    """Validate and convert timestamp"""
    if isinstance(timestamp, datetime):
        return timestamp
        
    try:
        return datetime.fromisoformat(timestamp)
    except (ValueError, TypeError):
        return None

def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate geographic coordinates"""
    return -90 <= lat <= 90 and -180 <= lng <= 180

# File: backend/app/utils/helpers.py

from typing import Any, Dict, List
import json
from datetime import datetime
from uuid import UUID

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling special types"""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

def format_error_response(
    error_code: int,
    message: str,
    details: Optional[Dict] = None
) -> Dict:
    """Format error response"""
    response = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow()
        }
    }
    
    if details:
        response["error"]["details"] = details
        
    return response

def paginate_results(
    items: List[Any],
    page: int = 1,
    page_size: int = 20
) -> Dict:
    """Paginate list of items"""
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        "items": items[start_idx:end_idx],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages
        }
    }

def clean_dict(d: Dict) -> Dict:
    """Remove None values from dictionary"""
    return {k: v for k, v in d.items() if v is not None}

# File: backend/app/utils/security.py

import secrets
import string
from typing import Tuple
import hashlib
import hmac

def generate_api_key() -> Tuple[str, str]:
    """Generate API key and secret"""
    # Generate random key
    alphabet = string.ascii_letters + string.digits
    key = ''.join(secrets.choice(alphabet) for _ in range(32))
    
    # Generate secret
    secret = secrets.token_hex(32)
    
    return f"opin_{key}", secret

def verify_webhook_signature(
    payload: str,
    signature: str,
    secret: str
) -> bool:
    """Verify webhook signature"""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)