"""Søge- og brand-endpoints der proxier OrbisX gennem vores eget API.

Dette er et tyndt lag på toppen af OrbisXClient. Senere udvider vi med
shared corpus-lookup (dedup på tværs af kunder) og vores egen ROI-logik.
"""

from collections import Counter

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.sources.orbisx import Article, OrbisXClient, SearchResponse, Site

router = APIRouter(prefix="/api", tags=["search"])


class OutletStat(BaseModel):
    site_name: str
    count: int


class BrandOverview(BaseModel):
    query: str
    total_matches: int
    sampled: int
    unique_outlets: int
    avg_time_on_frontpage: float
    free_pct: float
    top_outlets: list[OutletStat]
    recent_articles: list[Article]


@router.get("/sites", response_model=list[Site])
async def list_sites():
    """Liste over alle medier OrbisX overvåger."""
    async with OrbisXClient() as client:
        try:
            return await client.sites()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"OrbisX fejlede: {e}") from e


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Søgeord"),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    country: str | None = Query(None, description="Lande-kode, fx 'dk'"),
):
    """Søg artikler i OrbisX-corpus."""
    async with OrbisXClient() as client:
        try:
            return await client.search_articles(q, limit=limit, page=page, country=country)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"OrbisX fejlede: {e}") from e


@router.get("/brand/overview", response_model=BrandOverview)
async def brand_overview(
    q: str = Query(..., min_length=1, description="Brand-navn eller søgeord"),
    sample_size: int = Query(100, ge=10, le=200, description="Antal artikler at aggregere"),
    country: str | None = Query(None, description="Lande-kode, fx 'dk'"),
):
    """Aggregeret brand-overblik: top medier, gennemsnitlig forsidetid, nyeste artikler.

    Vi henter de seneste `sample_size` artikler og beregner statistik. `total_matches`
    er det fulde antal i OrbisX-corpus, ikke kun det vi har hentet.
    """
    async with OrbisXClient() as client:
        try:
            resp = await client.search_articles(q, limit=sample_size, page=1, country=country)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"OrbisX fejlede: {e}") from e

    articles = resp.results
    outlet_counts = Counter(a.site_name for a in articles)
    times = [a.time_on_frontpage for a in articles if a.time_on_frontpage is not None]
    avg_time = sum(times) / len(times) if times else 0.0
    free_count = sum(1 for a in articles if (a.availability or "").lower() == "free")
    free_pct = (free_count / len(articles) * 100) if articles else 0.0

    return BrandOverview(
        query=q,
        total_matches=resp.total_cluster_articles,
        sampled=len(articles),
        unique_outlets=len(outlet_counts),
        avg_time_on_frontpage=round(avg_time, 1),
        free_pct=round(free_pct, 1),
        top_outlets=[
            OutletStat(site_name=name, count=count)
            for name, count in outlet_counts.most_common(10)
        ],
        recent_articles=articles[:8],
    )
