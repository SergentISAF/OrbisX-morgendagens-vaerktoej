"""Simpel Redis-cache wrapper. Fejler graciously hvis Redis er nede."""

from __future__ import annotations

import logging

import redis.asyncio as redis

from app.core.config import settings

log = logging.getLogger(__name__)

_client: redis.Redis | None = None


def _get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


async def get_cache(key: str) -> str | None:
    try:
        return await _get_client().get(key)
    except Exception as e:
        log.warning("redis get failed for %s: %s", key, e)
        return None


async def set_cache(key: str, value: str, ttl_seconds: int = 600) -> None:
    try:
        await _get_client().set(key, value, ex=ttl_seconds)
    except Exception as e:
        log.warning("redis set failed for %s: %s", key, e)
