"""Redis-backed sliding-window rate limiter."""
import logging
import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)
_EXEMPT = {"/health", "/ready", "/metrics"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: str, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self._max = max_requests
        self._window = window_seconds

    async def dispatch(self, request: Request, call_next):
        if request.url.path in _EXEMPT:
            return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:{client_ip}:{int(time.time()) // self._window}"
        try:
            count = await self._redis.incr(key)
            if count == 1:
                await self._redis.expire(key, self._window * 2)
            if count > self._max:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                    detail=f"Rate limit exceeded: {self._max} req/{self._window}s")
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning("Rate limit check failed (allowing): %s", exc)
        return await call_next(request)
