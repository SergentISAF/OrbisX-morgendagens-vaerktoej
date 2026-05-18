"""Søge-endpoints der proxier OrbisX gennem vores eget API.

Dette er et tyndt lag på toppen af OrbisXClient. Senere udvider vi med
shared corpus-lookup (dedup på tværs af kunder) og vores egen ROI-logik.
"""

from fastapi import APIRouter, HTTPException, Query

from app.sources.orbisx import OrbisXClient, SearchResponse, Site

router = APIRouter(prefix="/api", tags=["search"])


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
