# Claude-instruks for OrbisX-morgendagens-værktøj

## Hvad er dette projekt
Plug-and-play medie-intelligence-motor. Backend (FastAPI) som andre plugger deres frontend ind i. Reference-dashboard er showcase, ikke produkt.

Læs `ROADMAP.md` først hver session. Især "Den simple version" øverst.

## Bruger
Dan er ide-person, ikke teknisk. Skriv kort, ingen jargon. Tag tekniske beslutninger for ham og orientér kort. Se memory `user_dan_non_technical_overview`.

## Kerneprincipper (må ikke brydes)
1. **Shared corpus** — artikler gemmes én gang, ikke per kunde
2. **Flotteste tallerken** — premium UX, Linear/Stripe-niveau
3. **Plug-and-play** — API er produktet, ikke dashboardet
4. **Interaktiv** — vi bliver del af kundens projekt, ikke et silo
5. **Lav cost** — minimér eksterne AI-calls, lokal AI hvor muligt

## Stack
- Backend: FastAPI + Postgres + Redis
- Frontend (showcase): Astro + React + Tailwind
- Deploy: docker-compose på NAS (kommer i fase 9)

## Vigtige mapper
- `api/` — backend (primært produkt)
- `reference-dashboard/` — showcase frontend
- `sdks/`, `embed/`, `docs-site/` — kommer senere
- `shared/openapi/orbisx-v2.json` — snapshot af OrbisX-API spec

## Kommandoer
```bash
make up        # Start alt med docker compose
make down      # Stop
make logs      # Se logs
make clean     # Slet data (volumes)
```

## Sprog
Skriv kommentarer og UI på dansk. Kode-identifikatorer på engelsk.
