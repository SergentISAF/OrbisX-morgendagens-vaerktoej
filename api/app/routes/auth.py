"""Auth-endpoints: signup, login, me."""

import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import CurrentUser
from app.core.security import create_token, hash_password, verify_password
from app.models import Tenant, User

router = APIRouter(prefix="/api/auth", tags=["auth"])


RELATIONSHIP_TYPES = {"sponsor", "sponseret", "mixed"}


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_name: str
    relationship_type: str = "sponsor"
    own_brand_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    tenant_id: int
    email: str
    tenant_name: str
    relationship_type: str
    own_brand_name: str | None


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "workspace"


def token_response(user: User, tenant: Tenant) -> TokenResponse:
    return TokenResponse(
        access_token=create_token(user.id, tenant.id),
        user_id=user.id,
        tenant_id=tenant.id,
        email=user.email,
        tenant_name=tenant.name,
        relationship_type=tenant.relationship_type,
        own_brand_name=tenant.own_brand_name,
    )


@router.post("/signup", response_model=TokenResponse)
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    if len(req.password) < 6:
        raise HTTPException(400, "Password skal være mindst 6 tegn")
    if req.relationship_type not in RELATIONSHIP_TYPES:
        raise HTTPException(400, f"relationship_type skal være en af {RELATIONSHIP_TYPES}")
    existing = (await db.execute(select(User).where(User.email == req.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(409, "Email findes allerede")

    base_slug = slugify(req.tenant_name)
    slug = base_slug
    i = 1
    while (await db.execute(select(Tenant).where(Tenant.slug == slug))).scalar_one_or_none():
        i += 1
        slug = f"{base_slug}-{i}"

    tenant = Tenant(
        name=req.tenant_name,
        slug=slug,
        relationship_type=req.relationship_type,
        own_brand_name=req.own_brand_name or req.tenant_name,
        own_brand_search_text=req.own_brand_name or req.tenant_name,
    )
    db.add(tenant)
    await db.flush()

    user = User(
        tenant_id=tenant.id,
        email=req.email,
        password_hash=hash_password(req.password),
        role="admin",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await db.refresh(tenant)

    return token_response(user, tenant)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == req.email))).scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Forkert email eller password")
    tenant = (await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))).scalar_one()
    return token_response(user, tenant)


class MeResponse(BaseModel):
    user_id: int
    tenant_id: int
    email: str
    tenant_name: str
    role: str
    relationship_type: str
    own_brand_name: str | None


@router.get("/me", response_model=MeResponse)
async def me(current: CurrentUser, db: AsyncSession = Depends(get_db)):
    tenant = (await db.execute(select(Tenant).where(Tenant.id == current.tenant_id))).scalar_one()
    return MeResponse(
        user_id=current.id,
        tenant_id=current.tenant_id,
        email=current.email,
        tenant_name=tenant.name,
        role=current.role,
        relationship_type=tenant.relationship_type,
        own_brand_name=tenant.own_brand_name,
    )


class TenantUpdate(BaseModel):
    relationship_type: str | None = None
    own_brand_name: str | None = None
    own_brand_search_text: str | None = None
    name: str | None = None


@router.patch("/tenant", response_model=MeResponse)
async def update_tenant(
    payload: TenantUpdate,
    current: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    tenant = (await db.execute(select(Tenant).where(Tenant.id == current.tenant_id))).scalar_one()
    if payload.relationship_type is not None:
        if payload.relationship_type not in RELATIONSHIP_TYPES:
            raise HTTPException(400, f"relationship_type skal være en af {RELATIONSHIP_TYPES}")
        tenant.relationship_type = payload.relationship_type
    if payload.own_brand_name is not None:
        tenant.own_brand_name = payload.own_brand_name.strip() or None
    if payload.own_brand_search_text is not None:
        tenant.own_brand_search_text = payload.own_brand_search_text.strip() or None
    if payload.name is not None:
        tenant.name = payload.name.strip() or tenant.name
    await db.commit()
    await db.refresh(tenant)
    return MeResponse(
        user_id=current.id,
        tenant_id=current.tenant_id,
        email=current.email,
        tenant_name=tenant.name,
        role=current.role,
        relationship_type=tenant.relationship_type,
        own_brand_name=tenant.own_brand_name,
    )
