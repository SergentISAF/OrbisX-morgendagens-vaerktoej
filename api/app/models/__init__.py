"""SQLAlchemy modeller for OrbisX-værktøj.

Fire kerne-tabeller:
- Tenant: kunde-firma (workspace)
- User: login (hører til Tenant)
- TrackedEntity: brand/sponsor/sponseret/konkurrent kunden overvåger
- Article: shared corpus (dedup på source_article_id)
- ArticleMatch: join — hvilke artikler er matchet for hvilken entity
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    users: Mapped[list["User"]] = relationship(back_populates="tenant")
    entities: Mapped[list["TrackedEntity"]] = relationship(back_populates="tenant")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="admin")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    tenant: Mapped[Tenant] = relationship(back_populates="users")


class TrackedEntity(Base):
    __tablename__ = "tracked_entities"
    __table_args__ = (UniqueConstraint("tenant_id", "name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    entity_type: Mapped[str] = mapped_column(
        String(20), default="brand"
    )  # brand|sponsor|sponseret|konkurrent
    search_text: Mapped[str] = mapped_column(String(500), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sponsor_link: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )  # navn på tilknyttet sponsor (frihåndstekst)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_match_count: Mapped[int] = mapped_column(Integer, default=0)

    tenant: Mapped[Tenant] = relationship(back_populates="entities")


class Article(Base):
    """Shared corpus — én artikel gemmes én gang, deles på tværs af kunder."""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_article_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )
    site_name: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_raw: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    time_on_frontpage: Mapped[int] = mapped_column(Integer, default=0)
    availability: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ArticleMatch(Base):
    """Hvilke artikler matcher hvilken entity — tenant-scoped link."""

    __tablename__ = "article_matches"
    __table_args__ = (UniqueConstraint("entity_id", "article_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("tracked_entities.id", ondelete="CASCADE"), nullable=False
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"), nullable=False
    )
    matched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
