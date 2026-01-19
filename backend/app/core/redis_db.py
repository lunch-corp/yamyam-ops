import logging

import redis
import redis.asyncio as aioredis

from app.core.config import settings


class RedisDatabase:
    def __init__(self):
        self.redis_url = settings.redis_url
        self._client: aioredis.Redis = None
        self._sync_client: redis.Redis = None

    async def get_client(self) -> aioredis.Redis:
        """Returns async Redis client"""
        if self._client is None:
            self._client = await aioredis.from_url(
                self.redis_url, decode_responses=True, max_connections=10
            )
        return self._client

    def get_sync_client(self) -> redis.Redis:
        """Returns synchronous Redis client"""
        if self._sync_client is None:
            self._sync_client = redis.from_url(
                self.redis_url, decode_responses=True, max_connections=10
            )
        return self._sync_client

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
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None


# global redis instance
redis_db = RedisDatabase()


def get_redis_client() -> redis.Redis:
    """Get synchronous Redis client (for use in sync contexts)"""
    return redis_db.get_sync_client()
