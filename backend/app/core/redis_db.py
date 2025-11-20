import os
import json
import logging
import subprocess

import redis.asyncio as aioredis
from app.core.config import settings
from app.services.redis_service import RedisService


class RedisDatabase:
    def __init__(self):
        self.redis_url = settings.redis_url
        self._client: aioredis.Redis = None
        self.service: RedisService = None

    async def get_client(self) -> aioredis.Redis:
        """Returns async Redis client"""
        if self._client is None:
            self._client = await aioredis.from_url(
                self.redis_url, decode_responses=True, max_connections=10
            )
        if self.service is None:
            self.service = RedisService(self._client)
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
            self.service = None

    async def initialize_data(self):
        try:
            host = os.getenv("REMOTE_JSON_HOST")
            port = os.getenv("REMOTE_JSON_PORT")
            user = os.getenv("REMOTE_JSON_USER")
            pw = os.getenv("REMOTE_JSON_PASS")
            remote_path = os.getenv("REMOTE_JSON_PATH")

            if not all([host, port, user, pw, remote_path]):
                logging.warning(
                    "Remote JSON server environment variables are not fully set"
                )
                return

            logging.info("Fetching similar restaurants JSON from remote server...")
            cmd = f"sshpass -p {pw} ssh -p {port} -o StrictHostKeyChecking=no {user}@{host} cat {remote_path}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=True
            )
            similar_data = json.loads(result.stdout)

            await self.get_client()
            if self.service:
                await self.service.load_similar_restaurants_data(
                    similar_data, from_memory=True
                )
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to fetch JSON from remote server: {e.stderr}")
        except Exception as e:
            logging.error(f"Redis data initialization error: {e}")


# Global Redis instance
redis_db = RedisDatabase()
