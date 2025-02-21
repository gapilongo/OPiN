# File: backend/app/core/cache.py

from typing import Optional, Any, Union
import json
from datetime import timedelta
import redis.asyncio as redis
from fastapi.encoders import jsonable_encoder

from app.core.config import settings

class CacheBackend:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Union[int, timedelta] = None
    ) -> bool:
        """Set value in cache"""
        try:
            serialized_value = json.dumps(jsonable_encoder(value))
            await self.redis.set(key, serialized_value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False

    async def increment(self, key: str) -> Optional[int]:
        """Increment counter"""
        try:
            return await self.redis.incr(key)
        except Exception as e:
            logger.error(f"Cache increment error: {str(e)}")
            return None

    async def expire(self, key: str, seconds: int) -> bool:
        """Set key expiration"""
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Cache expire error: {str(e)}")
            return False

# Example cache decorators
from functools import wraps
from hashlib import sha256

def cache_response(expire: int = 300):
    """Cache API response decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = sha256(":".join(key_parts).encode()).hexdigest()

            # Try to get from cache
            cache = CacheBackend()
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, expire)
            return result
        return wrapper
    return decorator


