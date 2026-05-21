"""Delbare rapport-links: tenant opretter token, public GET viser rapport."""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import CurrentUser
from app.models import ShareLink, Tenant, TrackedEntity
from app.routes.search import sponsorship_report

router = APIRouter(tags=["share"])


class ShareLinkResponse(BaseModel):
    token: str
    url: str
    entity_id: int
    created_at: datetime
    expires_at: datetime | None
    view_count: int


class SharedReport(BaseModel):
    sponsored_name: str
    sponsor_name: str | None
    color: str | None
    logo_url: str | None
    tenant_name: str
    report: dict
    view_count: int


@router.post("/api/entities/{entity_id}/share", response_model=ShareLinkResponse)
async def create_share_link(
    entity_id: int,
    current: CurrentUser,
    db: AsyncSession = Depends(get_db),
    days_valid: int | None = 365,
):
    entity = (
        await db.execute(
            select(TrackedEntity).where(
                TrackedEntity.id == entity_id,
                TrackedEntity.tenant_id == current.tenant_id,
            )
        )
    ).scalar_one_or_none()
    if not entity:
        raise HTTPException(404, "Entity ikke fundet")

    # Genbrug eksisterende aktivt link hvis muligt
    existing = (
        await db.execute(
            select(ShareLink).where(
                ShareLink.entity_id == entity_id,
                ShareLink.tenant_id == current.tenant_id,
            )
        )
    ).scalar_one_or_none()

    if existing:
        token = existing.token
        created_at = existing.created_at
        expires_at = existing.expires_at
        view_count = existing.view_count
    else:
        token = secrets.token_urlsafe(24)
        expires_at = (
            datetime.now(timezone.utc) + timedelta(days=days_valid)
            if days_valid
            else None
        )
        link = ShareLink(
            token=token,
            tenant_id=current.tenant_id,
            entity_id=entity_id,
            expires_at=expires_at,
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)
        created_at = link.created_at
        view_count = link.view_count

    return ShareLinkResponse(
        token=token,
        url=f"/shared?t={token}",
        entity_id=entity_id,
        created_at=created_at,
        expires_at=expires_at,
        view_count=view_count,
    )


@router.get("/api/shared/{token}", response_model=SharedReport)
async def get_shared_report(token: str, db: AsyncSession = Depends(get_db)):
    link = (
        await db.execute(select(ShareLink).where(ShareLink.token == token))
    ).scalar_one_or_none()
    if not link:
        raise HTTPException(404, "Linket findes ikke eller er udløbet")
    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(410, "Linket er udløbet")

    entity = (
        await db.execute(select(TrackedEntity).where(TrackedEntity.id == link.entity_id))
    ).scalar_one_or_none()
    if not entity:
        raise HTTPException(404, "Entity ikke fundet")
    tenant = (
        await db.execute(select(Tenant).where(Tenant.id == link.tenant_id))
    ).scalar_one()

    # Tæl visning op
    link.view_count += 1
    await db.commit()

    # Vi vil have AVE + top stories osv. Genbruger sponsorship_report-funktionen.
    report = await sponsorship_report(
        sponsored=entity.search_text,
        sponsor=entity.sponsor_link,
        sample_size=200,
        country=None,
    )

    return SharedReport(
        sponsored_name=entity.name,
        sponsor_name=entity.sponsor_link,
        color=entity.color,
        logo_url=entity.logo_url,
        tenant_name=tenant.name,
        report=report.model_dump(),
        view_count=link.view_count,
    )
