"""Søge- og brand-endpoints der proxier OrbisX gennem vores eget API.

Dette er et tyndt lag på toppen af OrbisXClient. Senere udvider vi med
shared corpus-lookup (dedup på tværs af kunder) og vores egen ROI-logik.
"""

import asyncio
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


class BrandShare(BaseModel):
    """En kortere variant til sammenligning på tværs af brands."""

    query: str
    total_matches: int
    sampled: int
    unique_outlets: int
    avg_time_on_frontpage: float
    top_outlets: list[OutletStat]
    share_pct: float


class CompareResponse(BaseModel):
    total_combined: int
    brands: list[BrandShare]


class AvailabilityStat(BaseModel):
    free: int
    paid: int


class SponsorshipReport(BaseModel):
    sponsored: str
    sponsor: str | None
    period_label: str
    total_matches: int
    sampled: int
    unique_outlets: int
    avg_time_on_frontpage: float
    median_time_on_frontpage: float
    total_time_on_frontpage: int
    availability: AvailabilityStat
    top_outlets: list[OutletStat]
    sample_articles: list[Article]
    co_mention_note: str


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


@router.get("/compare/overview", response_model=CompareResponse)
async def compare_overview(
    brands: list[str] = Query(..., description="2-5 brands at sammenligne"),
    sample_size: int = Query(50, ge=10, le=100),
    country: str | None = Query(None, description="Lande-kode, fx 'dk'"),
):
    """Side-by-side sammenligning af op til 5 brands med Share-of-Voice."""
    brands = [b.strip() for b in brands if b.strip()]
    if len(brands) < 2:
        raise HTTPException(400, "Mindst 2 brands skal angives")
    if len(brands) > 5:
        raise HTTPException(400, "Maksimalt 5 brands")

    async with OrbisXClient() as client:
        try:
            responses = await asyncio.gather(
                *[
                    client.search_articles(b, limit=sample_size, page=1, country=country)
                    for b in brands
                ]
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"OrbisX fejlede: {e}") from e

    total_combined = sum(r.total_cluster_articles for r in responses)
    results: list[BrandShare] = []
    for brand, resp in zip(brands, responses, strict=True):
        articles = resp.results
        outlet_counts = Counter(a.site_name for a in articles)
        times = [a.time_on_frontpage for a in articles if a.time_on_frontpage is not None]
        avg_time = sum(times) / len(times) if times else 0.0
        share = (
            (resp.total_cluster_articles / total_combined * 100)
            if total_combined > 0
            else 0.0
        )
        results.append(
            BrandShare(
                query=brand,
                total_matches=resp.total_cluster_articles,
                sampled=len(articles),
                unique_outlets=len(outlet_counts),
                avg_time_on_frontpage=round(avg_time, 1),
                top_outlets=[
                    OutletStat(site_name=name, count=count)
                    for name, count in outlet_counts.most_common(5)
                ],
                share_pct=round(share, 1),
            )
        )
    return CompareResponse(total_combined=total_combined, brands=results)


@router.get("/sponsorship/report", response_model=SponsorshipReport)
async def sponsorship_report(
    sponsored: str = Query(..., min_length=1, description="Sponseret entitet, fx 'Aalborg Håndbold'"),
    sponsor: str | None = Query(None, description="Sponsor-navn til rapport-header"),
    sample_size: int = Query(200, ge=50, le=500),
    country: str | None = Query(None, description="Lande-kode, fx 'dk'"),
):
    """Mediedækningsrapport for en sponseret entitet (klub, hold, event).

    Bruger PUBLIC OrbisX search. Co-mention med sponsor i artikel-tekst
    kræver fuld OrbisX cluster-adgang og kommer i en senere fase.
    """
    # Fetch flere sider parallelt for større sample
    pages_to_fetch = (sample_size + 99) // 100  # 100 per page max
    async with OrbisXClient() as client:
        try:
            responses = await asyncio.gather(
                *[
                    client.search_articles(
                        sponsored, limit=100, page=p, country=country
                    )
                    for p in range(1, pages_to_fetch + 1)
                ]
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"OrbisX fejlede: {e}") from e

    total = responses[0].total_cluster_articles if responses else 0
    articles: list[Article] = []
    for r in responses:
        articles.extend(r.results)
    articles = articles[:sample_size]

    outlet_counts = Counter(a.site_name for a in articles)
    times = [a.time_on_frontpage for a in articles if a.time_on_frontpage is not None]
    times_sorted = sorted(times)
    median = times_sorted[len(times_sorted) // 2] if times_sorted else 0
    total_time = sum(times)
    free = sum(1 for a in articles if (a.availability or "").lower() == "free")
    paid = sum(1 for a in articles if (a.availability or "").lower() == "paid")

    co_mention_note = (
        f"Sponsor-tagging ({sponsor}) i artikel-tekst kommer når vi har "
        "fuld OrbisX cluster-adgang. Denne rapport viser samlet mediedækning."
    ) if sponsor else (
        "Tilføj sponsor-navn i URL'en for at få sponsor-tagging "
        "(kræver fuld OrbisX-adgang)."
    )

    return SponsorshipReport(
        sponsored=sponsored,
        sponsor=sponsor,
        period_label=f"seneste {len(articles)} artikler",
        total_matches=total,
        sampled=len(articles),
        unique_outlets=len(outlet_counts),
        avg_time_on_frontpage=round(sum(times) / len(times), 1) if times else 0.0,
        median_time_on_frontpage=float(median),
        total_time_on_frontpage=int(total_time),
        availability=AvailabilityStat(free=free, paid=paid),
        top_outlets=[
            OutletStat(site_name=name, count=count)
            for name, count in outlet_counts.most_common(15)
        ],
        sample_articles=articles[:12],
        co_mention_note=co_mention_note,
    )
