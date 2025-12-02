import json
import logging
import os
import subprocess
from typing import Any, Optional


class RedisService:
    def __init__(self, redis_client, max_batch_size: int = 100):
        self.redis_client = redis_client
        self.max_batch_size = max_batch_size

    async def _get_client(self):
        # 이미 redis_client가 존재하면 그대로 반환
        return self.redis_client

    async def initialize_data(self):
        try:
            host = os.getenv("REMOTE_JSON_HOST")
            user = os.getenv("REMOTE_JSON_USER")
            pw = os.getenv("REMOTE_JSON_PASS")
            remote_path = os.getenv("REMOTE_JSON_PATH")

            if not all([host, user, pw, remote_path]):
                logging.warning(
                    "Remote JSON server environment variables are not fully set"
                )
                return {"error": "missing_env"}

            logging.info("Fetching similar restaurants JSON from remote server...")
            cmd = (
                f"sshpass -p {pw} ssh -p 10103 "
                f"-o StrictHostKeyChecking=no {user}@{host} cat {remote_path}"
            )

            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=True
            )
            similar_data = json.loads(result.stdout)

            # Load into Redis
            return await self.load_similar_restaurants_data(
                similar_data, from_memory=True
            )

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to fetch JSON from remote server: {e.stderr}")
            return {"error": "fetch_failed"}
        except Exception as e:
            logging.error(f"Redis data initialization error: {e}")
            return {"error": "unexpected_error"}

    async def create(
        self, items: dict[str, Any], expire: int | None = None
    ) -> dict[str, bool]:
        """
        Create key-value pairs in Redis. (Always uses pipeline)

        Args:
            items: {key: value} dictionary
            expire: TTL in seconds, None for no expiration

        Returns:
            {key: success} result dictionary
        """
        try:
            client = await self._get_client()
            items_list = list(items.items())
            total_items = len(items_list)
            results = {}

            # Process in chunks
            for i in range(0, total_items, self.max_batch_size):
                chunk = dict(items_list[i : i + self.max_batch_size])
                pipeline = client.pipeline()

                for key, value in chunk.items():
                    # Serialize dict or list to JSON
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)

                    pipeline.set(key, value)
                    if expire:
                        pipeline.expire(key, expire)

                # Execute pipeline
                await pipeline.execute()

                # Assume all keys in chunk succeeded
                for key in chunk.keys():
                    results[key] = True

                if total_items > self.max_batch_size:
                    logging.info(
                        f"Redis CREATE: Chunk {i // self.max_batch_size + 1} - {len(chunk)} keys"
                    )

            logging.info(f"Redis CREATE: Total {total_items} keys created")
            return results
        except Exception as e:
            logging.error(f"Redis create error: {e}")
            raise

    async def read(self, keys: list[str]) -> dict[str, Any]:
        """
        Read values from Redis by keys. (Always uses pipeline)

        Args:
            keys: List of keys to read

        Returns:
            {key: value} dictionary (non-existent keys return None)
        """
        try:
            client = await self._get_client()
            total_keys = len(keys)
            results = {}

            # Process in chunks
            for i in range(0, total_keys, self.max_batch_size):
                chunk_keys = keys[i : i + self.max_batch_size]

                # Read all at once with MGET
                values = await client.mget(chunk_keys)

                for key, value in zip(chunk_keys, values):
                    if value is None:
                        results[key] = None
                    else:
                        # Try to parse JSON
                        try:
                            results[key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            results[key] = value

                if total_keys > self.max_batch_size:
                    logging.info(
                        f"Redis READ: Chunk {i // self.max_batch_size + 1} - {len(chunk_keys)} keys"
                    )

            logging.info(f"Redis READ: Total {total_keys} keys read")
            return results
        except Exception as e:
            logging.error(f"Redis read error: {e}")
            raise

    async def update(
        self, items: dict[str, Any], expire: int | None = None
    ) -> dict[str, bool]:
        """
        Update existing key values in Redis. (Always uses pipeline)

        Args:
            items: {key: value} dictionary
            expire: TTL in seconds

        Returns:
            {key: success} result dictionary
        """
        try:
            client = await self._get_client()
            items_list = list(items.items())
            total_items = len(items_list)
            results = {}

            # Process in chunks
            for i in range(0, total_items, self.max_batch_size):
                chunk = dict(items_list[i : i + self.max_batch_size])
                pipeline = client.pipeline()

                for key, value in chunk.items():
                    # Check if key exists
                    exists = await client.exists(key)
                    if not exists:
                        results[key] = False
                        logging.warning(f"Redis UPDATE: key={key} does not exist")
                        continue

                    # Serialize dict or list to JSON
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)

                    pipeline.set(key, value)
                    if expire:
                        pipeline.expire(key, expire)
                    results[key] = True

                # Execute pipeline (only if there are keys to update)
                if any(results.get(k, False) for k in chunk.keys()):
                    await pipeline.execute()

                if total_items > self.max_batch_size:
                    logging.info(f"Redis UPDATE: Chunk {i // self.max_batch_size + 1}")

            successful = sum(1 for v in results.values() if v)
            logging.info(f"Redis UPDATE: {successful}/{total_items} keys updated")
            return results
        except Exception as e:
            logging.error(f"Redis update error: {e}")
            raise

    async def delete(self, keys: list[str]) -> dict[str, bool]:
        """
        Delete keys from Redis. (Always uses pipeline)

        Args:
            keys: List of keys to delete

        Returns:
            {key: success} result dictionary
        """
        try:
            client = await self._get_client()
            total_keys = len(keys)
            results = {}

            # Process in chunks
            for i in range(0, total_keys, self.max_batch_size):
                chunk_keys = keys[i : i + self.max_batch_size]
                existing_keys = []

                # Check existence of each key
                for key in chunk_keys:
                    exists = await client.exists(key)
                    if exists:
                        existing_keys.append(key)
                        results[key] = True
                    else:
                        results[key] = False

                # Delete only existing keys
                if existing_keys:
                    await client.delete(*existing_keys)

                if total_keys > self.max_batch_size:
                    logging.info(
                        f"Redis DELETE: Chunk {i // self.max_batch_size + 1} - {len(existing_keys)} deleted"
                    )

            total_deleted = sum(1 for v in results.values() if v)
            logging.info(f"Redis DELETE: {total_deleted}/{total_keys} keys deleted")
            return results
        except Exception as e:
            logging.error(f"Redis delete error: {e}")
            raise

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            client = await self._get_client()
            return bool(await client.exists(key))
        except Exception as e:
            logging.error(f"Redis exists error: {e}")
            raise

    async def get_ttl(self, key: str) -> int | None:
        """Get TTL of key (-1: no expiration, -2: key not found)"""
        try:
            client = await self._get_client()
            return await client.ttl(key)
        except Exception as e:
            logging.error(f"Redis ttl error: {e}")
            raise

    async def list_keys(self, pattern: str = "*") -> list[str]:
        """List keys matching pattern"""
        try:
            client = await self._get_client()
            return await client.keys(pattern)
        except Exception as e:
            logging.error(f"Redis keys error: {e}")
            raise

    async def bulk_create(
        self, items: dict[str, Any], expire: int | None = None
    ) -> dict[str, bool]:
        """
        Create multiple key-value pairs at once.
        Large batches are automatically split into chunks.

        Args:
            items: {key: value} dictionary
            expire: TTL in seconds applied to all keys

        Returns:
            {key: success} result dictionary
        """
        try:
            client = await self._get_client()

            # check batch size and split into chunks
            items_list = list(items.items())
            total_items = len(items_list)
            results = {}

            # process with split chunks
            for i in range(0, total_items, self.max_batch_size):
                chunk = dict(items_list[i : i + self.max_batch_size])
                pipeline = client.pipeline()

                for key, value in chunk.items():
                    # dict or list is json-serialized
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)

                    pipeline.set(key, value)
                    if expire:
                        pipeline.expire(key, expire)

                # execute pipeline
                await pipeline.execute()

                # mark as success for all chunks
                for key in chunk.keys():
                    results[key] = True

                logging.info(
                    f"Redis BULK CREATE: Chunk {i // self.max_batch_size + 1} - {len(chunk)} keys created"
                )

            logging.info(
                f"Redis BULK CREATE: Total {total_items} keys created in {(total_items + self.max_batch_size - 1) // self.max_batch_size} chunks"
            )
            return results
        except Exception as e:
            logging.error(f"Redis bulk create error: {e}")
            raise

    async def bulk_read(self, keys: list[str]) -> dict[str, Any]:
        """
        Read multiple key values at once.
        Large batches are automatically split into chunks.

        Args:
            keys: List of keys to read

        Returns:
            {key: value} dictionary (non-existent keys return None)
        """
        try:
            client = await self._get_client()
            total_keys = len(keys)
            results = {}

            # Process in chunks
            for i in range(0, total_keys, self.max_batch_size):
                chunk_keys = keys[i : i + self.max_batch_size]

                # Read all at once with MGET
                values = await client.mget(chunk_keys)

                for key, value in zip(chunk_keys, values):
                    if value is None:
                        results[key] = None
                    else:
                        # Try to parse JSON
                        try:
                            results[key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            results[key] = value

                logging.info(
                    f"Redis BULK READ: Chunk {i // self.max_batch_size + 1} - {len(chunk_keys)} keys read"
                )

            logging.info(
                f"Redis BULK READ: Total {total_keys} keys read in {(total_keys + self.max_batch_size - 1) // self.max_batch_size} chunks"
            )
            return results
        except Exception as e:
            logging.error(f"Redis bulk read error: {e}")
            raise

    async def bulk_update(
        self, items: dict[str, Any], expire: int | None = None
    ) -> dict[str, bool]:
        """
        Update multiple key values at once.
        Large batches are automatically split into chunks.

        Args:
            items: {key: value} dictionary
            expire: TTL in seconds applied to all keys

        Returns:
            {key: success} result dictionary
        """
        try:
            client = await self._get_client()
            items_list = list(items.items())
            total_items = len(items_list)
            results = {}

            # Process in chunks
            for i in range(0, total_items, self.max_batch_size):
                chunk = dict(items_list[i : i + self.max_batch_size])
                pipeline = client.pipeline()

                for key, value in chunk.items():
                    # Check if key exists
                    exists = await client.exists(key)
                    if not exists:
                        results[key] = False
                        logging.warning(f"Redis BULK UPDATE: key={key} does not exist")
                        continue

                    # Serialize dict or list to JSON
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)

                    pipeline.set(key, value)
                    if expire:
                        pipeline.expire(key, expire)
                    results[key] = True

                # Execute pipeline (only if there are keys to update)
                if any(results.get(k, False) for k in chunk.keys()):
                    await pipeline.execute()

                logging.info(
                    f"Redis BULK UPDATE: Chunk {i // self.max_batch_size + 1} - {sum(1 for k in chunk.keys() if results.get(k, False))} keys updated"
                )

            successful_updates = sum(1 for v in results.values() if v)
            logging.info(
                f"Redis BULK UPDATE: Total {successful_updates}/{total_items} keys updated"
            )
            return results
        except Exception as e:
            logging.error(f"Redis bulk update error: {e}")
            raise

    async def bulk_delete(self, keys: list[str]) -> dict[str, bool]:
        """
        Delete multiple keys at once.
        Large batches are automatically split into chunks.

        Args:
            keys: List of keys to delete

        Returns:
            {key: success} result dictionary
        """
        try:
            client = await self._get_client()
            total_keys = len(keys)
            results = {}

            # Process in chunks
            for i in range(0, total_keys, self.max_batch_size):
                chunk_keys = keys[i : i + self.max_batch_size]
                existing_keys = []

                # Check existence of each key
                for key in chunk_keys:
                    exists = await client.exists(key)
                    if exists:
                        existing_keys.append(key)
                        results[key] = True
                    else:
                        results[key] = False

                # Delete only existing keys
                if existing_keys:
                    await client.delete(*existing_keys)

                logging.info(
                    f"Redis BULK DELETE: Chunk {i // self.max_batch_size + 1} - {len(existing_keys)} keys deleted"
                )

            total_deleted = sum(1 for v in results.values() if v)
            logging.info(
                f"Redis BULK DELETE: Total {total_deleted}/{total_keys} keys deleted"
            )
            return results
        except Exception as e:
            logging.error(f"Redis bulk delete error: {e}")
            raise

    async def load_similar_restaurants_data(
        self, data: Optional[dict] = None, from_memory: bool = False
    ) -> dict[str, Any]:
        if not from_memory or not data:
            return {"loaded": 0, "skipped": 0, "error": "No data provided"}
        sample_key = "diner:2411227:similar_diner_ids"
        existing = await self.read([sample_key])
        if existing.get(sample_key) is not None:
            return {"loaded": 0, "skipped": 0, "already_exists": True}

        items = {
            f"diner:{rid}:similar_diner_ids": [v[0] for v in lst]
            for rid, lst in data.items()
        }
        results = await self.create(items, expire=None)
        succeeded = sum(1 for v in results.values() if v)
        failed = len(results) - succeeded
        return {"loaded": succeeded, "skipped": failed}
