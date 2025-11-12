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

    async def initialize_data(self):
        """Initialize Redis with similar restaurants data"""
        try:
            from pathlib import Path
            from app.services.redis_service import redis_service

            # Path to similar_restaurants.json
            data_path = Path("/app/data/similar_restaurants.json")

            if not data_path.exists():
                # Try alternative path (for local development)
                data_path = Path("data/similar_restaurants.json")

            if data_path.exists():
                logging.info("Initializing Redis with similar restaurants data...")
                stats = await redis_service.load_similar_restaurants_data(
                    str(data_path)
                )

                if stats.get("already_exists"):
                    logging.info("Similar restaurants data already exists in Redis")
                elif stats.get("error"):
                    logging.error(f"Failed to load data: {stats['error']}")
                else:
                    logging.info(f"Loaded {stats['loaded']} similar restaurant entries")
            else:
                logging.info(f"Similar restaurants data file not found at {data_path}")

        except Exception as e:
            logging.error(f"Redis data initialization error: {e}")


# Global Redis instance
redis_db = RedisDatabase()
