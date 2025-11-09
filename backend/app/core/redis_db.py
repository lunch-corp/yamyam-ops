import logging
from typing import Optional

import redis.asyncio as aioredis
from app.core.config import settings


class RedisDatabase:
    def __init__(self):
        self.redis_url = settings.redis_url
        self._client: Optional[aioredis.Redis] = None

    async def get_client(self) -> aioredis.Redis:
        """Returns async Redis client"""
        if self._client is None:
            self._client = await aioredis.from_url(
                self.redis_url, decode_responses=True, max_connections=10
            )
        return self._client

    async def ping(self) -> bool:
        """Check Redis connection status"""
        try:
            client = await self.get_client()
            return await client.ping()
        except Exception as e:
            logging.error(f"Redis ping error: {e}")
            return False

    async def close(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            self._client = None


# Global Redis instance
redis_db = RedisDatabase()
