# OrbisX — Morgendagens Værktøj — Roadmap

## Den simple version (start altid her)

**Hvad bygger vi?**
En motor som andre firmaer plugger ind i deres egen hjemmeside eller intranet og bruger til at se hvor meget deres brand, sponsorat eller konkurrent bliver omtalt i medierne. Tænk på det som "Stripe for medieovervågning": vi leverer dataen og kraften, kunden bygger sit eget look ovenpå.

**Hvor er vi nu?**
Planlægning. Ingen kode skrevet endnu. Vi venter på dig for at sige "byg".

**Næste tre skridt:**
1. Du afklarer med Orbis-teamet hvordan vi får adgang til API'et (én delt konto eller én per kunde).
2. Du fortæller mig hvad jeres GitHub-organisation hedder.
3. Når begge er klar, siger du "byg fase 1" og jeg sætter skelettet op.

**Hvis du vil dykke ned:**
Resten af dokumentet er teknisk og lang. Bare scroll. Du kan altid komme tilbage til denne sektion.

---

> **Sådan bruges dokumentet:** Start altid med "Den simple version" ovenfor. Detaljerne nedenfor er til reference når noget er uklart. Opdatér "Beslutnings-log" og "Opdateringer" når noget ændrer sig.

---

## Status

| Felt | Værdi |
|------|-------|
| Fase | Planning (ingen kode skrevet endnu) |
| Sidst opdateret | 2026-05-18 |
| Næste skridt | Afklar OrbisX-auth-model (org-konto vs per-kunde) før byggestart |
| Repo-navn | `OrbisX-morgendagens-værktøj` |
| GitHub-org | Orbis arbejds-org (præcist navn TBD) |
| Lokal sti | `/Users/dan/dev/OrbisX-morgendagens-værktøj` |

---

## Mission

**Vi laver backend som andre plugger deres frontend ind i.** Plug-and-play media-intelligence-motor som PR-bureauer, kommunikationsafdelinger og produkt-teams bygger deres egen tallerken ovenpå.

Vi leverer ROI-indsigt i reklame- og sponsorat-omtale gennem et veldokumenteret REST-API, SDK'er og embed-kit. Vores eget dashboard er reference/showcase — ikke produktet.

Tese: hvis vi er kraftig nok som motor og smukke nok som referenceimplementation, bliver vi bureauernes valg når de skal levere medierapporter til deres kunder.

---

## Forretningsmodel: Backend-as-Service (Plug-and-Play)

**Vi er Stripe/Algolia for medie-intelligence, ikke Mailchimp.**

### Tre integrationspaths for kunden

1. **Brug API'et direkte** — kunden har egen frontend/CMS, bygger sin egen UI ovenpå vores REST-endpoints. Vi giver dem OpenAPI-spec, SDK og docs.

2. **Drop ind med embed-kit** — kunden plopper et `<script>`-tag eller iframe i deres eksisterende intranet/Notion/whatever. Auto-opdaterende widgets med deres branding.

3. **Brug vores reference-dashboard** — for kunder uden devs. Vi hoster vores eget UI som "fuld løsning". Kan white-labeles.

Tre tilbud, samme motor.

### Hvad det betyder for produktet

| Surface | Status |
|---------|--------|
| **API** | Primært produkt. Stabil, versioneret, world-class docs. |
| **Python + TypeScript SDK** | First-class. Pip/npm. Examples. |
| **Embed-kit** | Vanilla JS-bundle + React-komponenter. CDN-distribueret. |
| **Reference-dashboard** | Showcase. Stadig "flotteste tallerken", men ikke det primære. |
| **Docs-site** | Developer experience er en produkt-surface i sig selv. |

### Hvad det betyder for prissætning (skitse — TBD)

- **Per-tenant + volumen** (ikke per-bruger). Kunden beslutter hvor mange deres user-base er.
- **Free tier** med rate limit til prototyping.
- **Bureau-tier** med multi-sub-tenant så bureauer kan re-sælge til deres kunder.

### Risiko at adressere

- **"Bare en API"-fælde:** Vi mister produkt-narrativ hvis reference-frontend ikke er smuk nok til at sælge sig selv. Flotteste Tallerken gælder stadig — for at API'et sælges.
- **Support-byrde:** Plug-and-play kræver excellent fejlmeldinger, examples og fora. Skal indregnes.

---

## Designprincip: Den Flotteste Tallerken

**Dette er den vigtigste differentiator.** Data kan andre også vise. Vi vinder på hvordan vi serverer den.

### Tre ufravigelige krav

1. **Flotteste tallerken.** Hvert dashboard, hver graf, hver email-rapport skal se stilfuld og lækker ud. Premium typografi, generøs whitespace, gennemtænkt farveskema. Inspiration: Linear, Stripe, Vercel-dashboard.

2. **Brugernem — kommer tilbage dagligt.** App'en skal være så letlæselig at en kommunikationschef åbner den hver morgen i 5 minutter:
   - Forsiden er "Dagens 3 ting", ikke en filterskov
   - Mobiloptimeret fra dag 1 (CEO'er læser på telefonen)
   - Onboarding på under 60 sekunder
   - Hver klik skal føles snappy (preloading, optimistic UI)

3. **Stilfuldt — ikke generisk.** Bespoke datavisualisering. Custom farvepalette per kunde-brand. Animationer der hjælper forståelse, ikke distraherer.

### Konkrete designvalg

| Element | Valg | Hvorfor |
|---------|------|---------|
| Frontend | Astro + React islands | Static-shell speed + rich interaktivitet hvor det betaler sig |
| Komponenter | shadcn/ui-style + Tailwind CSS | Premium look out-of-the-box, fuld customizability |
| Charts | Observable Plot eller ECharts (TBD ved fase 6) | Polished, ikke generisk Chart.js |
| Typografi | Inter (sans) + premium serif til headings | Testes: Fraunces, Source Serif, eller egen |
| Farver | Neutral grayscale + brand-accent. Dark mode dag 1. | Tidløst, lader data tale |
| Motion | CSS view transitions + Framer Motion (sparsomt) | Stilfuldt, ikke gimmicky |
| Iconer | Lucide eller Phosphor | Konsistent, ikke emoji |

Reference til Dans designsmag (fra `feedback_dan_design_taste_apps.md`): bold/geometric/premium, ikke hand-drawn. Aldrig overlappende tekst. Kopier reference 1:1 før kreativ frihed.

### Daily-Return-mekanismer

- **Morgenbrief-side** som default-landing efter login: "Siden i går: X nye omtaler, Y outlets, Z spikes"
- **Email-digest kl. 07:00** der trækker brugeren ind i app'en for detaljer
- **Smart notifikationer**: kun ved meningsfulde events (volume-spike >2σ, ny outlet, kritisk omtale)
- **Personal touch**: brugerens navn, brugerens brands fremhævet, hilsen tilpasset tidspunkt
- **Momentum-cues** subtile: "Du har tjekket coverage 12 dage i træk"
- **Hurtig værdi**: første relevante data inden onboarding er færdig

### Design-leveranser per fase

- **Fase 1 (Skelet):** Design system-grundlag på plads (farvepalette, typografi, spacing-skala, komponentbibliotek). Storybook eller equivalent.
- **Fase 6 (Værktøj #1):** Skal kunne stå alene som "kunde-klar" produktoplevelse. Hvis ikke flot nok her, fix før vi går videre til #2/#3.
- **Fase 9 (Deploy):** Onboarding-flow, morgenbrief, email-template alle polerede inden første kunde.

---

## Interaktivitetsprincip: Vi Bliver Del af Kundens Projekt

**Vi er ikke et silo-værktøj.** Kunder skal kunne *tage os med* ind i deres eksisterende arbejde og bruge os som substrat, ikke som en separat destination.

### Hvad det betyder konkret

1. **Multi-bruger fra dag 1.** Hver kunde-workspace har flere teammedlemmer. Roller: admin, editor, viewer. Audit-log over hvem har lavet hvad.

2. **Delbare share-links.** Hver dashboard, rapport eller artikelvisning har en flot, kort URL kunden kan dele:
   - Læseadgang uden login (token-baseret)
   - Udløbsdato valgfri
   - "Powered by OrbisX"-footer (let white-label-mulighed senere)

3. **Embed overalt.** Kunder kan embedde charts og widgets i deres egne værktøjer:
   - iFrame-snippet til Notion, Confluence, eget intranet
   - oEmbed-support til Slack/Teams-previews
   - Auto-opdaterende widgets (live data)

4. **Annotations på data.** Kunder markerer "dette er kampagne X" på timeline, "her startede sponsorat Y", "dette var krise-respons Z". Annotations vises på grafer og inkluderes i rapporter.

5. **Comments + mentions.** Diskuter direkte på en artikel, rapport eller datapunkt. `@mention` af kollega = email/Slack-notifikation.

6. **Integrationer der trækker os ind:**
   - Slack/Teams (push alerts til kanaler, slash-commands til quick-search)
   - Notion/Confluence (embeds + auto-opdaterede sider)
   - Webhooks (kunden bygger sin egen integration)
   - Google Slides/Keynote-eksport (én klik → flot slide til møde)
   - Calendar (sponsorat-start/slut som events)

7. **Public API for kunderne.** Vi eksponerer vores backend som dokumenteret REST + webhooks. Kunderne kan bygge ovenpå os.

8. **Eksport der bevarer interaktivitet:** Eksporter ikke kun PDF/CSV — også interaktive HTML-snapshots og delbare URL-fanger der ser ud som vores app.

### Hvad det betyder for fase-planen

- **Fase 3 (Auth + Tenants):** Multi-bruger + roller med det samme — ikke tilføjet senere.
- **Fase 6 (Værktøj #1):** Annotation-overlejring og share-link-knap er minimum-features, ikke nice-to-haves.
- **Fase 9 (Deploy):** Slack-integration + embed-snippet skal være klar til første kunde. Ikke fase 10.
- **Fase 10+ (Senere):** Google Slides-eksport, Notion-embed, webhook-API, public REST API.

### Risiko

Interaktivitet uden polish bliver støj. Sharing-links og comments skal være lige så smukke som dashboardet selv — ellers brydes Flotteste Tallerken-løftet.

---

## Kerneprincip: Shared Corpus

**Den vigtigste arkitekturbeslutning.** Vi laver ÉT fælles datalager der vokser med alle søgninger. Kunder får "udsigter" ind i det.

```
                  [SHARED CORPUS]
                        ↑
   ┌────────────────────┼────────────────────┐
   │                    │                    │
[OrbisX-feed]    [Fremtidige kilder]    [Fremtidige kilder]

   ↓ artikler gemmes ÉN gang, content-hash som nøgle

                  [AI-enrichment]
                        ↓
        sentiment, entities, sprog, topic
        — beregnes ÉN gang per artikel, gemmes for evigt

                        ↓
                  [Kunde-queries]
   Kunde A: brand="Carlsberg" + sponsorat="FCK"
   Kunde B: brand="Carlsberg" + konkurrenter=["Tuborg","Royal"]
   → matcher mod samme korpus, ingen ny scraping eller AI-call
```

**Konsekvens:**
- Hvis to kunder søger samme term: 0 ekstra API-calls, 0 ekstra AI-calls.
- Marginal cost per ny kunde går mod nul over tid.
- Vi rører **aldrig** AI-API'er til pr-artikel-arbejde.

---

## Tech Stack

| Lag | Valg | Hvorfor |
|-----|------|---------|
| Backend | Python + FastAPI | Stærk på data, Dan's primære stack |
| DB | Postgres | Multi-tenant fra dag 1, JSONB, row-level security |
| Cache | Redis | OrbisX-svar-cache, rate limiting |
| Frontend | Astro + React islands | Static-shell speed + rich interaktivitet (se Designprincip) |
| Komponenter | Tailwind CSS + shadcn/ui-stil | Premium look out-of-the-box |
| Charts | Observable Plot eller ECharts | Polished, ikke generisk Chart.js |
| Scheduler | APScheduler eller arq | Periodiske sync-jobs |
| Reverse proxy | Caddy | Auto-TLS, inspireret af `webhost-infrastructure` |
| Tunnel | Cloudflare Tunnel | Sikker eksponering uden åbne porte |
| Deploy | Docker Compose på NAS | Matcher Dan's eksisterende CT-mønstre |

**Vi bruger IKKE:** Kubernetes, serverless, microservices, GraphQL, exotiske framework. "Så nemt som muligt."

---

## Datakilder

### Fase 1 (MVP)
- **OrbisX v2 API** (150+ nyhedsmedier, multi-country)

### Fase 2+ (senere)
- Reddit (officielt API, gratis tier)
- YouTube Data API (titler + beskrivelser)
- Facebook public pages (kræver Meta-app-godkendelse, uger ventetid)
- Podcast-transskriptioner (dyrt — overvejes nøje)

Hver kilde bygges som **plugin** i `backend/app/sources/` så de kan tilføjes uden at røre kerne-logik.

---

## AI-Strategi

Princippet: AI-API-calls **kun** når det er strengt nødvendigt og giver høj værdi per call.

| Opgave | Hvor det kører | Cost-pattern |
|--------|----------------|--------------|
| Sentiment | Lokal model (Docker, HuggingFace) | Gratis efter setup |
| Entity extraction | Lokal spaCy/transformers | Gratis |
| Embeddings (lighed/clustering) | Lokal sentence-transformers | Gratis |
| Rapport-sammenfatning | Claude Haiku, batched, cache by hash | Lav cost, kun ved rapport-gen |
| Anomali-forklaring | Claude Haiku, on-demand | Lav cost, sjælden |

**Regel:** Vi rører aldrig eksterne AI-API'er til pr-artikel-arbejde. Lokal AI-container kører sentiment + embeddings på CPU.

---

## MVP — De Tre Værktøjer

Valgt fase 1-scope (2026-05-18). Alle tre er Tier 1 (kun OrbisX-data, ingen AI).

### Alle tre er den SAMME motor med forskellige briller

```
TrackedEntity = noget en kunde overvåger omtale af
  ├─ navn ("Carlsberg", "FCK", "Tuborg")
  ├─ type: brand | sponsor | sponseret | konkurrent
  ├─ keywords/regler
  └─ tilknyttet OrbisX-cluster

ArticleMatch = artikel-mention af en tracked entity
  ├─ artikel (delt corpus)
  ├─ entity (per kunde)
  └─ dato/kilde/land
```

| # | Værktøj | Hvad det viser | Entities |
|---|---------|----------------|----------|
| 1 | **Brand-monitor** | Alle artikler for ÉN entity, timeline + outlet-fordeling | 1× brand |
| 2 | **Sponsorat-tracker** | Artikler hvor TO entities optræder sammen, co-mention-graf | 1× sponsor + 1× sponseret |
| 3 | **Konkurrent-sammenligning** | Volume side-by-side for 2-5 entities | 2-5× brands/konkurrenter |

---

## Datamodel (forenklet)

Fire tabeller bærer hele MVP'en.

```
Tenant                    (kunde-firma)
 └─ User                  (login, hører til Tenant)
 └─ TrackedEntity         (Carlsberg, Tuborg, FCK...)
       └─ ArticleMatch    ← join til shared Article
            └─ Article    (delt corpus, dedup'd på content_hash)

Tool-konfig: hvilke entities indgår i hvilket værktøj, periode, filtre
```

Detaljeret skema designes i `docs/DATA-MODEL.md` ved fase 1.

---

## Repo-Struktur

Backend-as-Service-modellen reflekteres i mappestrukturen: `api/` er primært, `sdks/` + `embed/` er first-class, `reference-dashboard/` er showcase.

```
OrbisX-morgendagens-værktøj/
├── README.md
├── CLAUDE.md
├── ROADMAP.md                   ← du står her
├── docs/                        # Intern dokumentation
│   ├── ARCHITECTURE.md
│   ├── DATA-MODEL.md
│   ├── ROI-METHODOLOGY.md       (fase 4+)
│   └── ORBISX-API.md
├── api/                         # PRIMÆRT PRODUKT — REST API + worker
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── core/                # config, db, cache, auth (API-keys + JWT)
│   │   ├── routes/
│   │   │   ├── tenants.py
│   │   │   ├── entities.py      # TrackedEntity CRUD
│   │   │   ├── brand.py         # Værktøj #1 endpoints
│   │   │   ├── sponsorship.py   # Værktøj #2 endpoints
│   │   │   ├── compare.py       # Værktøj #3 endpoints
│   │   │   ├── webhooks.py      # Outbound webhooks til kunder
│   │   │   └── embed.py         # Token-gen til embed-widgets
│   │   ├── sources/
│   │   │   ├── base.py
│   │   │   └── orbisx.py        # Typed klient genereret fra openapi.json
│   │   ├── corpus/
│   │   │   ├── ingest.py
│   │   │   └── query.py
│   │   ├── models/
│   │   └── jobs/
│   ├── tests/
│   └── alembic/
├── sdks/                        # FIRST-CLASS — pip/npm install
│   ├── python/
│   │   ├── pyproject.toml
│   │   ├── orbisx/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── models.py
│   │   ├── examples/
│   │   └── tests/
│   └── typescript/
│       ├── package.json
│       ├── src/
│       ├── examples/
│       └── tests/
├── embed/                       # FIRST-CLASS — drop-in widgets
│   ├── package.json
│   ├── src/
│   │   ├── widgets/
│   │   │   ├── brand-monitor.tsx
│   │   │   ├── sponsorship-tracker.tsx
│   │   │   └── compare.tsx
│   │   ├── vanilla/             # <script>-bundle uden React-dep.
│   │   └── react/               # @orbisx/react NPM-pakke
│   └── examples/                # Notion, intranet, plain HTML
├── reference-dashboard/         # SHOWCASE — vores egen flotteste tallerken
│   ├── package.json
│   ├── astro.config.mjs
│   ├── src/
│   │   ├── pages/
│   │   │   ├── login.astro
│   │   │   ├── dashboard.astro
│   │   │   ├── brand/[id].astro
│   │   │   ├── sponsorship/[id].astro
│   │   │   └── compare/[id].astro
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   ├── filters/
│   │   │   └── entities/
│   │   └── lib/
│   └── public/
├── docs-site/                   # DEVELOPER EXPERIENCE — publiceret docs
│   ├── package.json
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.astro      # Landing
│   │   │   ├── quickstart.mdx
│   │   │   ├── guides/
│   │   │   ├── reference/       # Auto-gen fra OpenAPI
│   │   │   └── recipes/
│   │   └── components/
│   └── public/
├── infra/
│   ├── docker-compose.yml
│   ├── Caddyfile                # Cherry-pick fra webhost-infrastructure
│   └── cloudflare-tunnel.yml
├── shared/
│   └── openapi/
│       ├── orbisx-v2.json       # Snapshot af officiel OrbisX spec
│       └── our-api.json         # Vores egen API genereret
├── .github/workflows/
├── .env.example
├── .gitignore
└── Makefile
```

**Hvorfor mono-repo:** SDK'er, embed-kit og docs-site er afhængige af samme API-version. Mono-repo gør version-koordinering let. Hver mappe har sin egen `package.json`/`pyproject.toml` så de kan publiceres uafhængigt.

---

## Build-Sekvens

Hver fase = målbar leverance. Tjek af efterhånden.

- [ ] **Fase 0 — Afklaring** (før kode)
  - [ ] OrbisX-auth-model bekræftet med Orbis-team
  - [ ] Orbis GitHub-org-navn bekræftet
  - [ ] Domæne til dashboard valgt
  - [ ] OrbisX-cluster-strategi bekræftet (opretter vi clusters via API'et?)
- [ ] **Fase 1 — Skelet (Mono-repo)**
  - [ ] Repo oprettet på Orbis GitHub-org
  - [ ] Mono-repo struktur: `api/`, `sdks/python/`, `sdks/typescript/`, `embed/`, `reference-dashboard/`, `docs-site/`
  - [ ] docker-compose med Postgres + Redis kører lokalt
  - [ ] `api/`: FastAPI hello world + OpenAPI auto-spec
  - [ ] `reference-dashboard/`: Astro + React islands hello world
  - [ ] `docs-site/`: Astro/Starlight setup med OpenAPI-auto-render
  - [ ] Tailwind CSS + design-tokens (farver, spacing, typografi)
  - [ ] shadcn/ui-komponenter bootstrappet
  - [ ] Dark mode-skift virker
  - [ ] Storybook eller component-galleri
  - [ ] CI-pipeline (lint + tests per workspace)
- [ ] **Fase 2 — OrbisX-klient**
  - [ ] Typed Python-klient generet fra `openapi.json`
  - [ ] Test-call mod live OrbisX-endpoint
  - [ ] Klient gemt i `backend/app/sources/orbisx.py`
- [ ] **Fase 3 — Auth + Tenants (API-keys + JWT)**
  - [ ] API-key auth som primær (til SDK/embed/integration)
  - [ ] JWT som sekundær (til reference-dashboard login)
  - [ ] Tenant + User + Role-model (admin/editor/viewer)
  - [ ] API-key management UI i reference-dashboard
  - [ ] Rate limiting per API-key
  - [ ] Audit-log over kald
- [ ] **Fase 4 — TrackedEntity CRUD**
  - [ ] Backend API for CRUD
  - [ ] Frontend UI til at oprette/redigere entities
  - [ ] Validering + tests
- [ ] **Fase 5 — Sync-job**
  - [ ] Når entity oprettes → opret/find OrbisX-cluster
  - [ ] Pull artikler periodisk
  - [ ] Gem i shared corpus med dedup
  - [ ] Job-monitoring + retry-logik
- [ ] **Fase 6 — Værktøj #1: Brand-monitor (API + SDK + Embed + Dashboard)**
  - [ ] `api/`: Endpoints til volume-timeline, outlets, articles m. paginering
  - [ ] `sdks/python/` + `sdks/typescript/`: Auto-genererede klienter + examples
  - [ ] `embed/`: `<orbisx-brand-monitor>` web component + React-komponent
  - [ ] `reference-dashboard/`: Polished Observable Plot/ECharts visning
  - [ ] `docs-site/`: Brand-monitor-quickstart med kode-eksempler i 3 sprog
  - [ ] Mobil-layout testet i reference-dashboard og embed
  - [ ] Morgenbrief-widget på forsiden ("Siden i går: ...")
  - [ ] Kvalitets-review mod premium-reference (Linear/Stripe-niveau) — gate til fase 7
  - [ ] Første rigtig leverance til pilot-kunde
- [ ] **Fase 7 — Værktøj #2: Sponsorat-tracker**
  - [ ] Co-mention-logik
  - [ ] Sponsorat-dashboard (sponsor × sponseret over tid)
  - [ ] Sammenligning før/efter sponsorat-start
- [ ] **Fase 8 — Værktøj #3: Konkurrent-sammenligning**
  - [ ] Multi-entity overlay-graf
  - [ ] Share-of-Voice-beregning
  - [ ] Konkurrent-tabel
- [ ] **Fase 9 — Deploy + Daily-Return-polering**
  - [ ] Caddyfile + Cloudflare Tunnel-config
  - [ ] Deploy til NAS Docker-container
  - [ ] Domæne pegende på production
  - [ ] Backup-script til Postgres
  - [ ] Onboarding-flow under 60 sekunder, polished
  - [ ] Email-digest (kl. 07:00) med flot HTML-template
  - [ ] Smart-notifikations-logik (spike >2σ, kun meningsfulde)
  - [ ] Personal touch på morgenbrief (navn, hilsen, brands)
  - [ ] Loading-states + skeleton-screens overalt
  - [ ] Performance-pass (Lighthouse >90 på mobil)
  - [ ] Første kunde onboarded

---

## Åbne Spørgsmål

Skal afklares før de relevante faser starter.

| # | Spørgsmål | Skal afklares før | Status |
|---|-----------|-------------------|--------|
| 1 | OrbisX-auth-model: org-konto (vi som reseller) eller per-kunde-login? Specifikationen viser `securitySchemes: {}` og `security: None`. | Fase 1 | Åben |
| 2 | OrbisX GitHub-org-navn? | Fase 1 | Åben |
| 3 | Domæne til dashboard (orbis-roi.dk? internt orbis-domæne?) | Fase 9 | Åben |
| 4 | Branding: OrbisX-brandet, hvidmærket eller fælles? | Fase 6 | Åben |
| 5 | Cluster-strategi: opretter vi OrbisX-clusters via `POST /v2/clusters`, eller bruger vi `GET /v2/search/articles` direkte? | Fase 5 | Åben — anbefaling: opret clusters |
| 6 | Tenant-isolation på shared corpus: deler kunder labels/annotations, eller har hver kunde private overlejringer? | Fase 4 | Åben — anbefaling: shared corpus + private labels |
| 7 | Hvilke 3 KPIs på første dashboard-side? | Fase 6 | Foreslået: Volume, Top outlets, Geografisk fordeling |

---

## Beslutnings-Log

| Dato | Beslutning | Begrundelse |
|------|-----------|-------------|
| 2026-05-18 | Repo-navn `OrbisX-morgendagens-værktøj` med æ/ø | Dans valg, accepteret URL-konsekvenser |
| 2026-05-18 | Multi-tenant fra dag 1 | Matcher "fremtidens værktøj"-ambition |
| 2026-05-18 | Stack: Python + FastAPI + Postgres + Astro + Docker | Boring tech, lav cost, matcher Dan's eksisterende mønstre |
| 2026-05-18 | Shared Corpus-arkitektur | Eliminerer redundant scraping og AI-calls på tværs af kunder |
| 2026-05-18 | Fase 1-kilder: kun OrbisX | Hold scope stramt, andre kilder i fase 2+ |
| 2026-05-18 | Lokal AI (sentiment, embeddings) frem for eksterne API'er | Cost-besparelse, ingen pr-artikel-API-calls |
| 2026-05-18 | MVP = værktøj #1 + #2 + #3 | Samme motor, tre dashboard-sider, lavest risiko |
| 2026-05-18 | Cherry-pick fra `webhost-infrastructure`, ikke 1:1 kopi | Kun det vi har brug for |
| 2026-05-18 | **Forretningsmodel: Backend-as-Service (plug-and-play)** | Dan: "vi laver backend for din frontend plug and play". Vi er Stripe/Algolia-modellen, ikke Mailchimp |
| 2026-05-18 | Mono-repo med `api/`, `sdks/`, `embed/`, `reference-dashboard/`, `docs-site/` | Reflekterer at API + SDK + embed er first-class produkter, ikke kun frontend |
| 2026-05-18 | API-key auth primær, JWT sekundær | Plug-and-play kræver API-keys; dashboard-login er sekundært |
| 2026-05-18 | Reference-dashboard er showcase, ikke produkt | Vi konkurrerer ikke med bureauernes egne UI'er, vi er motoren under |
| 2026-05-18 | Design/UX kvalitet er primær differentiator ("flotteste tallerken") | Data kan andre vise — vi vinder på præsentation og daglig brugervenlighed |
| 2026-05-18 | Frontend skiftet fra Astro+HTMX til Astro+React islands | HTMX er ikke premium nok til "stilfuldt og lækkert"-niveau |
| 2026-05-18 | Charts: Observable Plot/ECharts, ikke Chart.js | Generisk Chart.js bryder premium-kravet |
| 2026-05-18 | Dark mode + mobiloptimering fra dag 1 | Daily-return kræver fleksibilitet i kontekst |

---

## Senere Værktøjer (efter MVP)

### Tier 1 — Ren OrbisX-data, ingen AI
- Share-of-Voice (afledt af #3)
- Kampagne-tracker (tidsvindue + keywords)
- Volume-spike-alert (Slack/Teams)
- Top-outlets-rapport
- Geografisk fordeling
- Trending-i-min-branche
- PDF-månedsrapport
- Executive Morning Brief
- RSS pr. kunde-segment
- Slack/Teams-integration
- Excel/CSV-export
- Semantisk søgning (OrbisX semantic-endpoint)
- Lignende-historier-finder

### Tier 2 — Kræver lokal AI
- Sentiment-trend
- Sentiment pr. outlet
- Krise-early-warning
- Topic-clustering
- Co-occurrence-graf
- Sentiment omkring event

### Tier 3 — Kræver kunde-data (outlets, rate-cards)
- Estimeret rækkevidde
- AVE (Annonceværdi-ækvivalent)
- Sponsorat-ROI med kr.-tal
- Kampagne-effekt-rapport med ROI

---

## Opdateringer

Hold log over hvad der ændres i denne fil.

| Dato | Hvad ændrede sig | Hvem |
|------|------------------|------|
| 2026-05-18 | Roadmap oprettet | Dan + Claude (planning-session) |
| 2026-05-18 | Tilføjet Designprincip-sektion ("Flotteste Tallerken"), frontend-stack skiftet, design-leveranser per fase | Dan markerede UX/design som primær differentiator |
| 2026-05-18 | Tilføjet Interaktivitetsprincip ("vi bliver del af kundens projekt") | Dan: vi skal være substrat, ikke silo |
| 2026-05-18 | Stort pivot: Forretningsmodel sat til Backend-as-Service plug-and-play. Mono-repo med api/sdks/embed/reference-dashboard/docs-site. Mission rewritten. | Dan: "Vi laver back end for din front end plug and play" |
