# OrbisX — Handoff til næste Claude-session

> Sidst opdateret: 2026-05-27. Dette er et komplet recap. Læs det først.

## TL;DR

Plug-and-play medie-intelligence-motor (Backend-as-Service ovenpå OrbisX v2 API). Web-dashboard som showcase + native iOS-app der bruger samme backend. Live siden 2026-05-18. Arbejdsnavn "OrbisX" — endeligt brand-navn ikke valgt.

Dan er ide-personen og ikke teknisk. Tag tekniske beslutninger, skriv kort, ingen jargon. ([[user_dan_non_technical_overview]])

## Status lige nu

- Backend kører på CT 105, port 8095, public via Tailscale Funnel
- iOS-app builder + archive succeeds, men er IKKE i TestFlight endnu
- 3 åbne tasks: TestFlight-opsætning, brand-navn-jagt, app.holmstadit.dk-routing
- Sidste arbejde: AVE-ranking på workspace-kort, share-links færdig

## Repos

| Repo | Sti | GitHub |
|------|-----|--------|
| Backend + web | `/Users/dan/dev/OrbisX-morgendagens-værktøj` | `SergentISAF/OrbisX-morgendagens-vaerktoej` (public) |
| iOS-app | `/Users/dan/dev/OrbisX-iOS` | `SergentISAF/OrbisX-iOS` (public) |

Begge er Dans personlige (SergentISAF), midlertidigt public for at CT 105 kan git-clone uden deploy-key. Skal flyttes tilbage til private senere.

## Live URLs

| Surface | URL |
|---------|-----|
| Web-dashboard | https://elpris-dashboard.tail330027.ts.net |
| API docs | https://elpris-dashboard.tail330027.ts.net/docs |
| Eksempel delt rapport | https://elpris-dashboard.tail330027.ts.net/shared?t=WsgXZ5eRQMCwH-RcYh5DaDDu2m_6Q3EO |
| OrbisX backend (ekstern) | https://yifub04z0f.execute-api.eu-north-1.amazonaws.com/v2 |
| Vesterlund-grundejerforening | https://vesterlund.holmstadit.dk (anden Dan-side, samme infra-mønster) |

## Vigtige filer at læse først

### I backend-repo
1. `ROADMAP.md` — masterplan, krydset af løbende
2. `CLAUDE.md` — projekt-instrukser
3. `docs/IOS-APP-PLAN.md` — iOS-app plan
4. `docs/NEXT-SESSION.md` — denne fil
5. `shared/openapi/orbisx-v2.json` — OrbisX API spec
6. `api/app/main.py` — FastAPI entry
7. `api/app/models/__init__.py` — datamodel (Tenant, User, TrackedEntity, Article, ArticleMatch, ShareLink)
8. `api/app/routes/` — endpoints (auth, entities, sync, search, share)
9. `api/app/services/ave.py` — AVE-beregning (outlet-tier × prominence)
10. `infra/docker-compose.prod.yml` — prod-stack
11. `infra/Caddyfile.prod` — internal reverse proxy
12. `reference-dashboard/src/pages/index.astro` — forside
13. `reference-dashboard/src/components/SponsorshipReport.tsx` — print-klar rapport
14. `reference-dashboard/src/components/SharedReportView.tsx` — public delt rapport

### I iOS-repo
1. `README.md`
2. `project.yml` — xcodegen-config (Bundle ID `dk.holmstadit.orbisx`, Team `58Z296VH22`)
3. `Sources/OrbisX/App.swift` — @main entry
4. `Sources/OrbisX/Network/APIClient.swift` — actor, JWT
5. `Sources/OrbisX/Network/Models.swift` — Codable matching backend
6. `Sources/OrbisX/Features/Auth/AuthStore.swift` — login/signup/tenant-update
7. `Sources/OrbisX/Features/Auth/LoginView.swift` — rolle-vælger på signup
8. `Sources/OrbisX/Features/Workspace/WorkspaceView.swift` — workspace + add-sheet + settings-sheet
9. `Sources/OrbisX/Features/EntityDetail/EntityDetailView.swift` — AVE-banner + share-link
10. `Sources/OrbisX/Utilities/Keychain.swift`
11. `Sources/OrbisX/Utilities/ShareSheet.swift`

### Eksternt
- PDF til Mikkel om backend-bugs: `~/Desktop/OrbisX-Mikkel-Bugs-2026-05-18.pdf`

## Memory-filer du SKAL læse for dette projekt

Læs i denne rækkefølge:
1. [[start-here]] — generel preflight til Dan
2. [[user_dan_non_technical_overview]] — Dan er ide-person, ikke teknisk
3. [[user_dan_adhd_hyperfocus]] — store leverancer, ikke kunstigt små
4. [[orbisx-morgendagens-vaerktoej]] — denne projekt-status
5. [[user_orbis_role]] — Dans rolle hos Orbis
6. [[orbis-team]] — Mikkel = backend/leder, email `Mikkel@orbisx.ai`
7. [[mac-mini-claude-code-setup]] — Mac mini er udviklingsmaskine (`mac-mini-dan`, 100.123.37.43)
8. [[webhost-ct]] — Caddy/Cloudflare Tunnel-setup på CT 108
9. [[apple-developer-account]] — `HolmstadIT@icloud.com`, Team `58Z296VH22`

### Feedback der ALTID gælder

- [[feedback_dan_scope_pragmatism]] — flag + Recommended + 2-3 alternatives, han vælger næsten altid Recommended
- [[feedback_pace_and_assumptions]] — ét trin ad gangen i Xcode/Apple-UI-flows
- [[feedback_asc_submit_dan_only]] — ASC submit-knapper klikker Claude ALDRIG
- [[feedback_dan_design_taste_apps]] — bold/geometric/premium, ikke hand-drawn
- [[feedback_no_em_dash]] — ingen em-dash i tekst, brug komma
- [[feedback_memory_search_before_write]] — grep memory før ny fil

## Tech-stack one-liner

Python 3.12 + FastAPI + Postgres + Redis + Caddy / Astro + React + Tailwind / SwiftUI + Keychain. Deploy via docker-compose på Proxmox-LXC.

## Datamodel kerne

```
Tenant (relationship_type: sponsor|sponseret, own_brand_name)
 └─ User (email, password_hash, JWT-auth)
 └─ TrackedEntity (name, entity_type, color, sponsor_link, last_match_count, last_ave_dkk)
       └─ ArticleMatch
            └─ Article (shared corpus, dedup'd på source_article_id)
 └─ ShareLink (token, entity_id, view_count, expires_at)
```

## Beslutninger (alle 2026-05-18 medmindre andet)

- Forretningsmodel: Backend-as-Service plug-and-play
- Mono-repo backend + separat iOS-repo
- Multi-tenant fra dag 1
- Stack: boring tech (FastAPI + Astro + SwiftUI)
- AVE-beregning som tier × prominence
- Sponsor er en rolle, ikke et felt per entity
- Workspace sorteres efter AVE (ikke match-count)
- Share-links token-baseret, 365 dages udløb
- Repo public midlertidigt (deploy-key kommer senere)
- TestFlight først til Mikkel, App Store senere
- Brand-navn skal vælges før App Store-submission
- Consumer/Press-fase noteret som 10+

## Næste skridt (åbne tasks)

**Task #3: TestFlight-konfiguration**
Backend + iOS er klar. Archive bygges OK. Mangler:
1. Dan opretter app i App Store Connect: appstoreconnect.apple.com → Apps → + → New App. Bundle ID `dk.holmstadit.orbisx`, navn "OrbisX", primary lang Danish, SKU `orbisx-v1`
2. Når oprettet: jeg uploader archive via Xcode Organizer eller `xcrun altool`
3. Tilføj Mikkel + tidlige kunder som internal testers

**Task #4: Brand-navn-jagt**
Glimt.com er taget (registreret 1999, ejer fornyede april 2026). Tidligere fundet ledige men ingen talte til Dan: glimva, klippora, klangra, bragra. Skal være vælges før App Store-submission. Brug ordentlig WHOIS-check (`whois.verisign-grs.com` port 43, ikke gh-CLI's status).

**Bonus: app.holmstadit.dk-routing**
Cloudflare Zero Trust → Networks → Tunnels → `holmstad-webhost` → Public Hostnames → tilføj `app.holmstadit.dk` → service `http://192.168.10.56:8095`. Dan tager dialogen.

## Apple Developer

- Team ID: `58Z296VH22`
- Konto: HolmstadIT@icloud.com
- Cert allerede installeret på Mac mini (Apple Development: Dan Kristoffer Holmstad)
- Bundle ID `dk.holmstadit.orbisx` auto-oprettet ved første archive

## Begrænsninger (Mikkel-rapport sendt)

OrbisX-backend har 5 endpoints der fejler 500. Blokerer:
- Cluster-baseret artikel-adgang (brødtekst → ægte co-mention)
- Dato-filter (periode-rapporter)
- Trending stories, volume metadata, semantisk søgning
Workaround: vi bruger public search-endpoint og pre-computer AVE per sync. Når Mikkel fixer bugs får vi mere data uden ændringer i vores backend-kontrakt.

## Operations

### Genstart backend på CT 105
```bash
ssh root@192.168.10.86 "pct exec 105 -- bash -c 'cd /root/apps/OrbisX-morgendagens-vaerktoej && git pull && cd infra && docker compose -f docker-compose.prod.yml up -d --build api dashboard'"
```

### Bygge iOS-app
```bash
cd /Users/dan/dev/OrbisX-iOS && xcodegen generate && open OrbisX.xcodeproj
```

### Test backend lokalt (kræver Docker)
```bash
cd /Users/dan/dev/OrbisX-morgendagens-værktøj && make up
# Dashboard på localhost:4321, API på localhost:8000
```

### Genberegn AVE for eksisterende entities
Swipe på entity i iOS-app → "Sync" — eller via API:
```bash
curl -X POST -H "Authorization: Bearer <token>" \
  https://elpris-dashboard.tail330027.ts.net/api/entities/<id>/sync
```

## Hvordan Dan vil samarbejde

- Få ord, ingen jargon
- Tag tekniske beslutninger, orientér kort
- Store leverancer er OK (ADHD/hyperfokus)
- Brand-navn / business / retning beslutter han
- "Det som du anbefaler" → bare gør det
- Apple Dev og ASC-klik tager han selv
- Sig "klar" / "fortsætt" — det betyder han er klar til næste trin

## Hvis noget er gået galt

- Backend nede? `ssh root@192.168.10.86 "pct exec 105 -- docker ps"` viser status
- iOS build fejler? Tjek diagnostics — SourceKit gnider, men `xcodebuild build` viser sandheden
- OrbisX returnerer 500? Det er flaky, retry 2-3 gange før konklusion
- Repo skal pulles på CT 105 efter push: se "Operations" ovenfor
