from fastapi import Request, HTTPException
from app.core.cache import CacheBackend
from app.core.config import settings

class RateLimiter:
    def __init__(
        self,
        requests: int = 100,
        window: int = 60
    ):
        self.requests = requests
        self.window = window
        self.cache = CacheBackend()

    async def __call__(
        self,
        request: Request,
        call_next
    ):
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not await self._check_rate_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )

        return await call_next(request)

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (IP or API key)"""
        if api_key := request.headers.get("X-API-Key"):
            return f"api:{api_key}"
        return f"ip:{request.client.host}"

    async def _check_rate_limit(self, client_id: str) -> bool:
        """Check if request is within rate limit"""
        key = f"rate_limit:{client_id}"
        
        # Increment request counter
        requests = await self.cache.increment(key)
        if requests == 1:
            # Set expiry for new keys
            await self.cache.expire(key, self.window)
            return True

        return requests <= self.requests