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


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_name: str


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


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "workspace"


@router.post("/signup", response_model=TokenResponse)
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    if len(req.password) < 6:
        raise HTTPException(400, "Password skal være mindst 6 tegn")
    existing = (await db.execute(select(User).where(User.email == req.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(409, "Email findes allerede")

    base_slug = slugify(req.tenant_name)
    slug = base_slug
    i = 1
    while (await db.execute(select(Tenant).where(Tenant.slug == slug))).scalar_one_or_none():
        i += 1
        slug = f"{base_slug}-{i}"

    tenant = Tenant(name=req.tenant_name, slug=slug)
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

    return TokenResponse(
        access_token=create_token(user.id, tenant.id),
        user_id=user.id,
        tenant_id=tenant.id,
        email=user.email,
        tenant_name=tenant.name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == req.email))).scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Forkert email eller password")
    tenant = (await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))).scalar_one()
    return TokenResponse(
        access_token=create_token(user.id, user.tenant_id),
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        tenant_name=tenant.name,
    )


class MeResponse(BaseModel):
    user_id: int
    tenant_id: int
    email: str
    tenant_name: str
    role: str


@router.get("/me", response_model=MeResponse)
async def me(current: CurrentUser, db: AsyncSession = Depends(get_db)):
    tenant = (await db.execute(select(Tenant).where(Tenant.id == current.tenant_id))).scalar_one()
    return MeResponse(
        user_id=current.id,
        tenant_id=current.tenant_id,
        email=current.email,
        tenant_name=tenant.name,
        role=current.role,
    )
