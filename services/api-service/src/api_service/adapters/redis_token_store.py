"""Redis token blacklist."""
import redis.asyncio as aioredis
from api_service.interfaces.i_token_store import ITokenStore


class RedisTokenStore(ITokenStore):
    def __init__(self, redis_url: str):
        self._redis = aioredis.from_url(redis_url, decode_responses=True)

    async def blacklist(self, token: str, ttl_seconds: int) -> None:
        await self._redis.setex(f"bl:{token}", ttl_seconds, "1")

    async def is_blacklisted(self, token: str) -> bool:
        return await self._redis.exists(f"bl:{token}") > 0
