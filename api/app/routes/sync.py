"""Sync-endpoint: hent OrbisX-artikler for en TrackedEntity og gem i shared corpus.

Indtil OrbisX cluster-adgang er åbnet bruger vi public search-endpoint
og dedup på source_article_id.
"""

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import CurrentUser
from app.models import Article, ArticleMatch, TrackedEntity
from app.sources.orbisx import OrbisXClient

router = APIRouter(prefix="/api/entities", tags=["sync"])


class SyncResult(BaseModel):
    entity_id: int
    articles_fetched: int
    articles_new: int
    matches_new: int
    last_synced_at: datetime


@router.post("/{entity_id}/sync", response_model=SyncResult)
async def sync_entity(
    entity_id: int,
    current: CurrentUser,
    db: AsyncSession = Depends(get_db),
    sample_size: int = 200,
):
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

    pages = (sample_size + 99) // 100
    async with OrbisXClient() as client:
        results = await asyncio.gather(
            *[
                client.search_articles(e.search_text, limit=100, page=p)
                for p in range(1, pages + 1)
            ],
            return_exceptions=True,
        )

    fetched = []
    for r in results:
        if not isinstance(r, Exception):
            fetched.extend(r.results)

    # Strict phrase-filter for fler-ord
    if len(e.search_text.strip().split()) >= 2:
        needle = e.search_text.lower()
        filtered = [
            a
            for a in fetched
            if needle in ((a.article_title or "") + " " + (a.frontpage_title or "")).lower()
        ]
        if filtered:
            fetched = filtered

    # Upsert artikler — undgå dubletter på source_article_id
    new_articles = 0
    article_id_by_source: dict[int, int] = {}
    for a in fetched:
        existing = (
            await db.execute(select(Article).where(Article.source_article_id == a.article_id))
        ).scalar_one_or_none()
        if existing:
            article_id_by_source[a.article_id] = existing.id
        else:
            row = Article(
                source_article_id=a.article_id,
                site_name=a.site_name,
                title=a.article_title,
                url=a.article_url,
                created_raw=a.article_created,
                time_on_frontpage=a.time_on_frontpage or 0,
                availability=a.availability,
            )
            db.add(row)
            await db.flush()
            article_id_by_source[a.article_id] = row.id
            new_articles += 1

    # Opret ArticleMatch — på conflict ignore
    new_matches = 0
    for source_id, article_id in article_id_by_source.items():
        stmt = pg_insert(ArticleMatch).values(
            tenant_id=current.tenant_id,
            entity_id=e.id,
            article_id=article_id,
        ).on_conflict_do_nothing(index_elements=["entity_id", "article_id"])
        result = await db.execute(stmt)
        if result.rowcount and result.rowcount > 0:
            new_matches += 1

    e.last_synced_at = datetime.now(timezone.utc)
    e.last_match_count = len(article_id_by_source)
    await db.commit()
    await db.refresh(e)

    return SyncResult(
        entity_id=e.id,
        articles_fetched=len(fetched),
        articles_new=new_articles,
        matches_new=new_matches,
        last_synced_at=e.last_synced_at,
    )
