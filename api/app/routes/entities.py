"""TrackedEntity CRUD — tenant-scoped."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import CurrentUser
from app.models import TrackedEntity

router = APIRouter(prefix="/api/entities", tags=["entities"])

ENTITY_TYPES = {"brand", "sponsor", "sponseret", "konkurrent"}


class EntityIn(BaseModel):
    name: str
    entity_type: str = "brand"
    search_text: str | None = None  # default = name
    color: str | None = None
    logo_url: str | None = None
    sponsor_link: str | None = None


class EntityOut(BaseModel):
    id: int
    name: str
    entity_type: str
    search_text: str
    color: str | None
    logo_url: str | None
    sponsor_link: str | None
    created_at: datetime
    last_synced_at: datetime | None
    last_match_count: int


@router.get("", response_model=list[EntityOut])
async def list_entities(current: CurrentUser, db: AsyncSession = Depends(get_db)):
    # Sortér efter eksponering (last_match_count) faldende, så top-værdi for kunden står øverst
    q = (
        select(TrackedEntity)
        .where(TrackedEntity.tenant_id == current.tenant_id)
        .order_by(TrackedEntity.last_match_count.desc(), TrackedEntity.created_at.desc())
    )
    return [EntityOut.model_validate(e, from_attributes=True) for e in (await db.execute(q)).scalars()]


@router.post("", response_model=EntityOut, status_code=201)
async def create_entity(
    payload: EntityIn,
    current: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    if payload.entity_type not in ENTITY_TYPES:
        raise HTTPException(400, f"entity_type skal være en af {ENTITY_TYPES}")
    e = TrackedEntity(
        tenant_id=current.tenant_id,
        name=payload.name.strip(),
        entity_type=payload.entity_type,
        search_text=(payload.search_text or payload.name).strip(),
        color=payload.color,
        logo_url=payload.logo_url,
        sponsor_link=payload.sponsor_link,
    )
    db.add(e)
    try:
        await db.commit()
        await db.refresh(e)
    except Exception:
        await db.rollback()
        raise HTTPException(409, "Entity med dette navn findes allerede i din workspace")
    return EntityOut.model_validate(e, from_attributes=True)


@router.delete("/{entity_id}", status_code=204)
async def delete_entity(
    entity_id: int,
    current: CurrentUser,
    db: AsyncSession = Depends(get_db),
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
        raise HTTPException(404, "Ikke fundet")
    await db.delete(e)
    await db.commit()
