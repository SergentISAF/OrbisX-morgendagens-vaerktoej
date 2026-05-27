"""OrbisX v2 API klient.

Wrapper omkring https://yifub04z0f.execute-api.eu-north-1.amazonaws.com/v2.
Auth-header gøres konfigurerbar — i øjeblikket virker de fleste read-endpoints
uden auth, men vi sender en API-key hvis settings.orbisx_api_key er sat.
"""

from __future__ import annotations

import asyncio

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


class DailyVolume(BaseModel):
    date: str
    articles: int
    minutes_on_frontpage: int = 0


class MetadataResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    total_articles: int = 0
    total_minutes_on_frontpage: int = 0
    daily: list[DailyVolume] = Field(default_factory=list)


class TrendingStory(BaseModel):
    model_config = ConfigDict(extra="allow")

    thread_id: int | None = None
    title: str | None = None
    url: str | None = None
    site_count: int | None = None
    article_count: int | None = None
    expected_views: int | None = None
    latest_created: str | None = None


class TrendingResponse(BaseModel):
    stories: list[TrendingStory] = Field(default_factory=list)


class ClusterSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    user_cluster_id: int
    cluster_id: int | None = None
    title: str | None = None
    cluster_type: str | None = None


class ClustersResponse(BaseModel):
    user_id: str
    results: list[ClusterSummary] = Field(default_factory=list)


class ClusterArticlesResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    user_id: str
    user_cluster_id: int
    results: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


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
        retries: int = 2,
    ) -> SearchResponse:
        """Søg artikler. Auto-retry på 5xx (OrbisX har flaky backend lige nu)."""
        params: dict[str, str | int] = {"query": query, "limit": limit, "page": page}
        if country:
            params["country"] = country

        last_err: Exception | None = None
        for attempt in range(retries + 1):
            try:
                r = await self._client.get("/search/articles", params=params)
                r.raise_for_status()
                return SearchResponse.model_validate(r.json())
            except httpx.HTTPStatusError as e:
                if 500 <= e.response.status_code < 600 and attempt < retries:
                    await asyncio.sleep(0.5 + attempt * 1.0)
                    last_err = e
                    continue
                raise
            except (httpx.TimeoutException, httpx.RequestError) as e:
                if attempt < retries:
                    await asyncio.sleep(0.5 + attempt * 1.0)
                    last_err = e
                    continue
                raise
        if last_err:
            raise last_err
        raise RuntimeError("Unreachable")

    async def similar_articles(self, article_id: int, limit: int = 10) -> SearchResponse:
        r = await self._client.get(
            f"/search/articles/{article_id}/similar", params={"limit": limit}
        )
        r.raise_for_status()
        return SearchResponse.model_validate(r.json())

    # ---- Platform: volume + trending (Mikkel-fix 2026-05-27) ----

    async def metadata(
        self,
        keywords: list[str],
        *,
        country: str = "dk",
        timerange: int | None = 30,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> MetadataResponse:
        """Daily volume for nøgleord. Brug timerange (dage) ELLER start/end_date."""
        body: dict = {"country": country, "keywords": keywords}
        if start_date and end_date:
            body["start_date"] = start_date
            body["end_date"] = end_date
        elif timerange is not None:
            body["timerange"] = timerange
        r = await self._client.post("/platform/metadata", json=body)
        r.raise_for_status()
        return MetadataResponse.model_validate(r.json())

    async def trending(
        self, *, country: str = "dk", timerange: int = 2, limit: int = 10
    ) -> TrendingResponse:
        """Trending stories på tværs af landet."""
        body = {"country": country, "timerange": timerange, "limit": limit}
        r = await self._client.post("/platform/trending", json=body)
        r.raise_for_status()
        return TrendingResponse.model_validate(r.json())

    # ---- User clusters (Mikkel-fix 2026-05-27) ----

    async def user_clusters(self, user_id: int) -> ClustersResponse:
        r = await self._client.get(f"/users/{user_id}/clusters")
        r.raise_for_status()
        return ClustersResponse.model_validate(r.json())

    async def cluster_articles(
        self, user_id: int, cluster_id: int
    ) -> ClusterArticlesResponse:
        r = await self._client.get(
            f"/users/{user_id}/clusters/{cluster_id}/articles"
        )
        r.raise_for_status()
        return ClusterArticlesResponse.model_validate(r.json())
