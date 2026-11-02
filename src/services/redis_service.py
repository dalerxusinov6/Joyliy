"""Redis Service providing distributed locking, caching, and task coordination with graceful in-memory fallback."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, Any, AsyncIterator

from src.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """
    Manages Redis connection, distributed locks, and caching.
    Automatically falls back to in-memory primitives when Redis is not configured or unavailable.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis = None
        self._is_connected = False
        self._local_locks: dict[str, asyncio.Lock] = {}
        self._local_cache: dict[str, tuple[float, Any]] = {}

    async def get_client(self):
        """Return connected Redis client, or None if unavailable."""
        if not self.redis_url:
            return None

        if self._redis is None:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=3,
                    socket_timeout=3,
                )
                await self._redis.ping()
                self._is_connected = True
                logger.info("Connected to Redis at %s", self.redis_url)
            except Exception as e:
                logger.warning("Redis connection failed (%s); using in-memory fallback: %s", self.redis_url, e)
                self._redis = None
                self._is_connected = False
        return self._redis

    @asynccontextmanager
    async def lock(self, name: str, timeout: int = 120) -> AsyncIterator[bool]:
        """
        Distributed lock context manager.
        Uses Redis SETNX with expiration when available, otherwise falls back to local asyncio.Lock.
        """
        lock_key = f"joyliy:lock:{name}"
        client = await self.get_client()

        if client and self._is_connected:
            token = f"{time.time()}"
            acquired = False
            try:
                # Attempt to acquire lock with expiry
                acquired = await client.set(lock_key, token, ex=timeout, nx=True)
                yield bool(acquired)
            finally:
                if acquired:
                    try:
                        # Release lock only if we still hold it
                        current_val = await client.get(lock_key)
                        if current_val == token:
                            await client.delete(lock_key)
                    except Exception as rel_err:
                        logger.debug("Error releasing Redis lock %s: %s", lock_key, rel_err)
        else:
            # In-memory fallback
            if name not in self._local_locks:
                self._local_locks[name] = asyncio.Lock()
            lock = self._local_locks[name]
            async with lock:
                yield True

    async def get_cached(self, key: str) -> Optional[Any]:
        """Get cached value by key."""
        client = await self.get_client()
        if client and self._is_connected:
            try:
                val = await client.get(f"joyliy:cache:{key}")
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.debug("Redis cache get error for %s: %s", key, e)
        else:
            if key in self._local_cache:
                expires_at, val = self._local_cache[key]
                if time.time() < expires_at:
                    return val
                else:
                    del self._local_cache[key]
        return None

    async def set_cached(self, key: str, value: Any, ttl_seconds: int = 120) -> None:
        """Store value in cache with TTL."""
        client = await self.get_client()
        if client and self._is_connected:
            try:
                payload = json.dumps(value)
                await client.setex(f"joyliy:cache:{key}", ttl_seconds, payload)
            except Exception as e:
                logger.debug("Redis cache set error for %s: %s", key, e)
        else:
            self._local_cache[key] = (time.time() + ttl_seconds, value)

    async def clear_cache(self, pattern: str = "*") -> None:
        """Clear cached entries."""
        client = await self.get_client()
        if client and self._is_connected:
            try:
                keys = await client.keys(f"joyliy:cache:{pattern}")
                if keys:
                    await client.delete(*keys)
            except Exception as e:
                logger.debug("Redis clear cache error: %s", e)
        self._local_cache.clear()


redis_service = RedisService()

