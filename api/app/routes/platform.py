"""Platform-endpoints: volume + trending.

Bruger OrbisX' /platform/metadata + /platform/trending (Mikkel fixede 2026-05-27).
Cached i Redis for at undgå genberegning og spare upstream-kald.
"""

import hashlib
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import CurrentUser
from app.core.redis_cache import get_cache, set_cache
from app.models import TrackedEntity
from app.sources.orbisx import OrbisXClient

router = APIRouter(prefix="/api", tags=["platform"])


class VolumePoint(BaseModel):
    date: str
    articles: int
    minutes_on_frontpage: int = 0


class VolumeResponse(BaseModel):
    entity_id: int
    keyword: str
    total_articles: int
    total_minutes_on_frontpage: int
    timerange_days: int
    daily: list[VolumePoint]


class TrendingStory(BaseModel):
    thread_id: int | None = None
    title: str | None = None
    url: str | None = None
    site_count: int | None = None
    article_count: int | None = None
    expected_views: int | None = None
    latest_created: str | None = None


class TrendingResponse(BaseModel):
    fetched_at: datetime
    country: str
    timerange_days: int
    stories: list[TrendingStory]


def _cache_key(*parts: str) -> str:
    raw = ":".join(parts)
    return "platform:" + hashlib.sha256(raw.encode()).hexdigest()[:24]


@router.get("/entities/{entity_id}/volume", response_model=VolumeResponse)
async def entity_volume(
    entity_id: int,
    current: CurrentUser,
    db: AsyncSession = Depends(get_db),
    days: int = 30,
):
    """Daily mention-volume for entity over N dage."""
    if days < 1 or days > 365:
        raise HTTPException(400, "days skal være mellem 1 og 365")

    e = (
        await db.execute(
            select(TrackedEntity).where(
                TrackedEntity.id == entity_id,
                TrackedEntity.tenant_id == current.tenant_id,
            )
        )
    ).scalar_one_or_none()
    if not e:
        raise HTTPException(404, "Entity ikke fundet")

    key = _cache_key("volume", e.search_text, str(days))
    cached = await get_cache(key)
    if cached:
        data = json.loads(cached)
        return VolumeResponse(entity_id=entity_id, **data)

    async with OrbisXClient() as client:
        meta = await client.metadata(
            keywords=[e.search_text], country="dk", timerange=days
        )

    payload = {
        "keyword": e.search_text,
        "total_articles": meta.total_articles,
        "total_minutes_on_frontpage": meta.total_minutes_on_frontpage,
        "timerange_days": days,
        "daily": [
            VolumePoint(
                date=d.date,
                articles=d.articles,
                minutes_on_frontpage=d.minutes_on_frontpage,
            ).model_dump()
            for d in meta.daily
        ],
    }
    await set_cache(key, json.dumps(payload), ttl_seconds=900)  # 15 min
    return VolumeResponse(entity_id=entity_id, **payload)


@router.get("/trending", response_model=TrendingResponse)
async def trending(
    current: CurrentUser,
    days: int = 2,
    limit: int = 10,
    country: str = "dk",
):
    """Trending stories på tværs af medierne (cached 10 min)."""
    if days < 1 or days > 30:
        raise HTTPException(400, "days skal være mellem 1 og 30")
    if limit < 1 or limit > 50:
        raise HTTPException(400, "limit skal være mellem 1 og 50")

    key = _cache_key("trending", country, str(days), str(limit))
    cached = await get_cache(key)
    if cached:
        data = json.loads(cached)
        return TrendingResponse(**data)

    async with OrbisXClient() as client:
        res = await client.trending(country=country, timerange=days, limit=limit)

    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "country": country,
        "timerange_days": days,
        "stories": [TrendingStory(**s.model_dump()).model_dump() for s in res.stories],
    }
    await set_cache(key, json.dumps(payload), ttl_seconds=600)
    return TrendingResponse(**payload)
