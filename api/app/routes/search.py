"""Søge- og brand-endpoints der proxier OrbisX gennem vores eget API.

Dette er et tyndt lag på toppen af OrbisXClient. Senere udvider vi med
shared corpus-lookup (dedup på tværs af kunder) og vores egen ROI-logik.
"""

import asyncio
import csv
import io
import re
from collections import Counter

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.ave import article_ave, ave_summary, tier_for_outlet
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


class AveBreakdown(BaseModel):
    total_dkk: int
    avg_per_article_dkk: int
    sample_size: int
    tier_distribution: dict[str, int]


class CoMention(BaseModel):
    sponsor_total_matches: int
    sponsor_sampled: int
    intersection_count: int
    intersection_pct_of_sponsored_sample: float
    intersection_articles: list[Article]
    intersection_ave_dkk: int
    method: str


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
    top_stories: list[Article]
    sample_articles: list[Article]
    ave_sample: AveBreakdown
    ave_extrapolated_dkk: int
    co_mention: CoMention | None
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
    pages_to_fetch = (sample_size + 99) // 100  # 100 per page max

    async def fetch_all_pages(query: str) -> tuple[int, list[Article]]:
        async with OrbisXClient() as c:
            results = await asyncio.gather(
                *[
                    c.search_articles(query, limit=100, page=p, country=country)
                    for p in range(1, pages_to_fetch + 1)
                ],
                return_exceptions=True,
            )
        valid = [r for r in results if not isinstance(r, Exception)]
        if not valid:
            raise next(r for r in results if isinstance(r, Exception))
        total_count = valid[0].total_cluster_articles
        arts: list[Article] = []
        for r in valid:
            arts.extend(r.results)
        return total_count, arts[:sample_size]

    try:
        if sponsor:
            (total, articles), (sponsor_total, sponsor_articles) = await asyncio.gather(
                fetch_all_pages(sponsored), fetch_all_pages(sponsor)
            )
        else:
            total, articles = await fetch_all_pages(sponsored)
            sponsor_total, sponsor_articles = 0, []
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OrbisX fejlede: {e}") from e

    # Hvis sponsored-navnet er fler-ord (fx "Aalborg Håndbold"), filtrer hårdt:
    # kun artikler hvor den FULDE frase optræder i titel/frontpage-titel.
    # Det fjerner artikler der bare matcher hvert ord for sig (fx "håndbold-stjerner i Aalborg").
    def has_phrase_in_title(a: Article, phrase: str) -> bool:
        title_text = ((a.article_title or "") + " " + (a.frontpage_title or "")).lower()
        return phrase.lower() in title_text

    sponsored_is_phrase = len(sponsored.strip().split()) >= 2
    if sponsored_is_phrase and articles:
        original_sample_size = len(articles)
        articles_strict = [a for a in articles if has_phrase_in_title(a, sponsored)]
        if articles_strict:
            # Estimer den "rigtige" total: oprindelig total × ratio af strict til pre-filter
            ratio = len(articles_strict) / original_sample_size
            total = max(int(total * ratio), len(articles_strict))
            articles = articles_strict

    outlet_counts = Counter(a.site_name for a in articles)
    times = [a.time_on_frontpage for a in articles if a.time_on_frontpage is not None]
    times_sorted = sorted(times)
    median = times_sorted[len(times_sorted) // 2] if times_sorted else 0
    total_time = sum(times)
    free = sum(1 for a in articles if (a.availability or "").lower() == "free")
    paid = sum(1 for a in articles if (a.availability or "").lower() == "paid")

    # Co-mention via titel-tekst-match med ord-grænser (undgår fx "OL" matching
    # i "politikere"). Blandt sponserede artikler finder vi dem hvor sponsorens
    # navn også står i titlen, og omvendt. Union = co-mention-kandidater.
    co_mention: CoMention | None = None
    if sponsor:
        def text_of(a: Article) -> str:
            return ((a.article_title or "") + " " + (a.frontpage_title or "")).lower()

        # Word-boundary regex for hver term (escape special chars)
        sponsor_pat = re.compile(r"\b" + re.escape(sponsor.lower()) + r"\b")
        sponsored_pat = re.compile(r"\b" + re.escape(sponsored.lower()) + r"\b")

        in_sponsored = [a for a in articles if sponsor_pat.search(text_of(a))]
        in_sponsor = [a for a in sponsor_articles if sponsored_pat.search(text_of(a))]
        seen: set[int] = set()
        unique: list[Article] = []
        for a in in_sponsored + in_sponsor:
            if a.article_id not in seen:
                seen.add(a.article_id)
                unique.append(a)

        pct = (len(unique) / len(articles) * 100) if articles else 0.0
        co_mention_ave = ave_summary(unique)
        co_mention = CoMention(
            sponsor_total_matches=sponsor_total,
            sponsor_sampled=len(sponsor_articles),
            intersection_count=len(unique),
            intersection_pct_of_sponsored_sample=round(pct, 1),
            intersection_articles=unique[:12],
            intersection_ave_dkk=co_mention_ave["total_dkk"],
            method=(
                f"Co-mention findes ved titel-tekst-match mellem '{sponsored}' og '{sponsor}'. "
                f"Sample: {sample_size} artikler per term. Brødtekst-baseret co-mention "
                "(mere nøjagtigt) venter på OrbisX cluster-adgang."
            ),
        )

    co_mention_note = (
        f"Co-mention med '{sponsor}' bruger artikel-intersection mellem to "
        "OrbisX-søgninger. For fuld brødtekst-baseret co-mention kræves "
        "OrbisX cluster-adgang (kommer når Orbis-teamet har fixet backend-bugs)."
    ) if sponsor else (
        "Tilføj sponsor-navn for at få co-mention mellem sponseret og sponsor."
    )

    ave_data = ave_summary(articles)
    if len(articles) > 0 and total > 0:
        extrapolated = int(ave_data["avg_per_article_dkk"] * total)
    else:
        extrapolated = 0

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
        top_stories=sorted(
            articles,
            key=lambda a: a.time_on_frontpage or 0,
            reverse=True,
        )[:5],
        sample_articles=articles[:12],
        ave_sample=AveBreakdown(**ave_data),
        ave_extrapolated_dkk=extrapolated,
        co_mention=co_mention,
        co_mention_note=co_mention_note,
    )


@router.get("/sponsorship/report.csv")
async def sponsorship_report_csv(
    sponsored: str = Query(..., min_length=1),
    sample_size: int = Query(200, ge=50, le=500),
    country: str | None = Query(None),
):
    """CSV-eksport af artikel-data til rapporten. Bruges af kunde-analytikere."""
    pages_to_fetch = (sample_size + 99) // 100

    async with OrbisXClient() as client:
        results = await asyncio.gather(
            *[
                client.search_articles(sponsored, limit=100, page=p, country=country)
                for p in range(1, pages_to_fetch + 1)
            ],
            return_exceptions=True,
        )

    responses = [r for r in results if not isinstance(r, Exception)]
    if not responses:
        first_err = next((r for r in results if isinstance(r, Exception)), None)
        raise HTTPException(status_code=502, detail=f"OrbisX fejlede: {first_err}")

    articles: list[Article] = []
    for r in responses:
        articles.extend(r.results)
    articles = articles[:sample_size]

    # Anvend strict phrase-filter for fler-ord-søgninger
    if len(sponsored.strip().split()) >= 2:
        articles = [
            a for a in articles
            if sponsored.lower() in ((a.article_title or "") + " " + (a.frontpage_title or "")).lower()
        ] or articles

    # Skriv CSV
    buf = io.StringIO()
    buf.write("﻿")  # BOM så Excel læser æøå korrekt
    writer = csv.writer(buf, delimiter=";")
    writer.writerow([
        "article_id",
        "site_name",
        "outlet_tier",
        "article_title",
        "article_url",
        "article_created",
        "time_on_frontpage_hours",
        "availability",
        "ave_dkk",
    ])
    for a in articles:
        writer.writerow([
            a.article_id,
            a.site_name,
            tier_for_outlet(a.site_name),
            a.article_title or "",
            a.article_url,
            a.article_created or "",
            a.time_on_frontpage or 0,
            a.availability or "",
            article_ave(a),
        ])

    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", sponsored).strip("_") or "rapport"
    filename = f"orbisx-{safe_name}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
