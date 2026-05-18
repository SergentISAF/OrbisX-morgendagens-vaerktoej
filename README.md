# OrbisX-morgendagens-værktøj

> Arbejdsnavn. Endeligt brand-navn vælges senere.

Plug-and-play medie-intelligence-motor. Backend som andre plugger deres frontend ind i.

**Start altid med [ROADMAP.md](ROADMAP.md) — første afsnit "Den simple version".**

## Hurtig start (lokal udvikling)

```bash
docker compose -f infra/docker-compose.yml up
```

Dette starter:
- **Postgres** (port 5432) — vores database
- **Redis** (port 6379) — cache
- **API** (port 8000) — FastAPI backend. Docs: http://localhost:8000/docs
- **Dashboard** (port 4321) — Astro reference-frontend. http://localhost:4321

Stop med `Ctrl+C`. Slet data med `docker compose -f infra/docker-compose.yml down -v`.

## Mapper

| Mappe | Hvad |
|-------|------|
| `api/` | FastAPI backend (primært produkt) |
| `reference-dashboard/` | Astro + React + Tailwind frontend (showcase) |
| `sdks/python/` | Python SDK (kommer i fase 2) |
| `sdks/typescript/` | TypeScript SDK (kommer i fase 2) |
| `embed/` | Drop-in widgets (kommer i fase 6) |
| `docs-site/` | Developer-docs (kommer i fase 2) |
| `infra/` | Docker, Caddy, Cloudflare Tunnel |
| `docs/` | Intern dokumentation |
| `shared/openapi/` | OpenAPI-spec snapshots |
