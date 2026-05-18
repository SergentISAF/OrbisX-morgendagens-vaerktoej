"""OrbisX v2 API klient.

Wrapper omkring https://yifub04z0f.execute-api.eu-north-1.amazonaws.com/v2.
Auth-header gøres konfigurerbar — i øjeblikket virker de fleste read-endpoints
uden auth, men vi sender en API-key hvis settings.orbisx_api_key er sat.
"""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import settings


class Article(BaseModel):
    model_config = ConfigDict(extra="allow")

    article_id: int
    site_name: str
    article_url: str
    article_title: str | None = None
    frontpage_title: str | None = None
    article_created: str | None = None
    availability: str | None = None
    time_on_frontpage: int | None = None
    inactive: int | None = None


class SearchResponse(BaseModel):
    results: list[Article]
    total_cluster_articles: int = 0


class Site(BaseModel):
    value: str
    label: str


class HealthResponse(BaseModel):
    status: str
    version: str | None = None


class OrbisXClient:
    """Asynk klient mod OrbisX v2 API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = (base_url or settings.orbisx_api_base).rstrip("/")
        self.api_key = api_key or settings.orbisx_api_key
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._default_headers(),
        )

    def _default_headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    async def __aenter__(self) -> "OrbisXClient":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    # ---- Platform endpoints ----

    async def health(self) -> HealthResponse:
        r = await self._client.get("/health")
        r.raise_for_status()
        return HealthResponse.model_validate(r.json())

    async def sites(self) -> list[Site]:
        r = await self._client.get("/platform/sites")
        r.raise_for_status()
        return [Site.model_validate(s) for s in r.json()]

    async def models(self) -> dict[str, str]:
        r = await self._client.get("/platform/models")
        r.raise_for_status()
        return r.json()

    # ---- Search endpoints ----

    async def search_articles(
        self,
        query: str,
        *,
        limit: int = 20,
        page: int = 1,
        country: str | None = None,
    ) -> SearchResponse:
        params: dict[str, str | int] = {"query": query, "limit": limit, "page": page}
        if country:
            params["country"] = country
        r = await self._client.get("/search/articles", params=params)
        r.raise_for_status()
        return SearchResponse.model_validate(r.json())

    async def similar_articles(self, article_id: int, limit: int = 10) -> SearchResponse:
        r = await self._client.get(
            f"/search/articles/{article_id}/similar", params={"limit": limit}
        )
        r.raise_for_status()
        return SearchResponse.model_validate(r.json())
