"""
Redis Client for Caching and Rate Limiting
Centralized Redis connection management
"""

import json
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings


class RedisClient:
    """Async Redis client wrapper"""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Establish Redis connection"""
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from Redis

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.redis:
            return None

        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis

        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds

        Returns:
            bool: True if successful
        """
        if not self.redis:
            return False

        if expire is None:
            expire = settings.REDIS_CACHE_TTL

        if not isinstance(value, str):
            value = json.dumps(value)

        return await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str) -> bool:
        """
        Delete key from Redis

        Args:
            key: Cache key

        Returns:
            bool: True if deleted
        """
        if not self.redis:
            return False

        return await self.redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists

        Args:
            key: Cache key

        Returns:
            bool: True if exists
        """
        if not self.redis:
            return False

        return await self.redis.exists(key) > 0

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment counter

        Args:
            key: Counter key
            amount: Amount to increment

        Returns:
            int: New value
        """
        if not self.redis:
            return 0

        return await self.redis.incrby(key, amount)

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration on key

        Args:
            key: Cache key
            seconds: Expiration time in seconds

        Returns:
            bool: True if successful
        """
        if not self.redis:
            return False

        return await self.redis.expire(key, seconds)

    async def get_keys(self, pattern: str) -> list:
        """
        Get keys matching pattern

        Args:
            pattern: Key pattern (e.g., "user:*")

        Returns:
            list: List of matching keys
        """
        if not self.redis:
            return []

        return await self.redis.keys(pattern)

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Key pattern

        Returns:
            int: Number of keys deleted
        """
        if not self.redis:
            return 0

        keys = await self.get_keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0

    async def set_hash(self, key: str, field: str, value: Any) -> bool:
        """
        Set hash field value

        Args:
            key: Hash key
            field: Field name
            value: Field value

        Returns:
            bool: True if successful
        """
        if not self.redis:
            return False

        if not isinstance(value, str):
            value = json.dumps(value)

        return await self.redis.hset(key, field, value)

    async def get_hash(self, key: str, field: str) -> Optional[Any]:
        """
        Get hash field value

        Args:
            key: Hash key
            field: Field name

        Returns:
            Field value or None
        """
        if not self.redis:
            return None

        value = await self.redis.hget(key, field)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def get_all_hash(self, key: str) -> dict:
        """
        Get all hash fields and values

        Args:
            key: Hash key

        Returns:
            dict: Hash data
        """
        if not self.redis:
            return {}

        return await self.redis.hgetall(key)


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """
    Dependency for getting Redis client

    Returns:
        RedisClient: Redis client instance
    """
    return redis_client
