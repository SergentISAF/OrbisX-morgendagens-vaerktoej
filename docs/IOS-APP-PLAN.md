# OrbisX iOS — Plan

> Native iOS-app der bruger samme backend som web-dashboardet. Bygges når brand-navn er valgt.

## Den simple version

**Hvem:** Marketing/PR/sponsorat-ansvarlige.
**Hvornår:** I køen, før et møde, i bilen.
**Hvad:** "Hvordan står mit brand lige nu?" — én tap, ét tal.

## Beslutninger truffet 2026-05-19

| Hvad | Valg |
|------|------|
| Repo-struktur | Separat repo (matcher Vaken-App-mønstret) |
| Distribution | TestFlight først til Mikkel + tidlige kunder. App Store senere. |
| Brand-navn | Skal være valgt FØR App Store-submission (anmeldelse hænger på det) |
| Platform | iOS først (SwiftUI, Mac mini med Xcode 26.4.1 klar) |
| Målgruppe | B2B |
| Killer use | On-the-go brand-check |

## Tech-stack

- **UI:** SwiftUI
- **Concurrency:** async/await + Task
- **Networking:** URLSession + Codable (matcher vores Pydantic-modeller)
- **Auth:** Bearer JWT (samme token som web), gemt i Keychain
- **Local state:** Ingen DB i V1 — vi henter live fra API. Måske SwiftData senere til offline-cache.
- **Build:** Xcode på Mac mini (`mac-mini-dan`)

## Tre kerneskærme i V1

### 1. Workspace (forsiden)
Liste over brugerens entities som kort med:
- Navn + farve-prik
- Total omtaler
- Ændring siden i går (+12, -3)
- Tap → entity-detalje

### 2. Entity-detalje
- AVE-banner (hero-tallet)
- Top 3 historier (klik åbner Safari)
- Top 5 medier
- Pull-to-refresh trigger sync

### 3. Hurtig-rapport
- Share-sheet integration: send AVE + top 3 historier til hovedsponsor via iMessage/email/AirDrop
- Genererer hurtig PDF eller delbar URL fra web-rapport

## iOS-specifikke fordele over web

- **Hjemmeskærms-widget:** AVE-tal direkte på lock screen
- **Push-notifikation kl. 07:00:** "Siden i går: X nye omtaler"
- **Haptik på pull-to-refresh**
- **Quick Look (long-press):** 5 nyeste artikler uden at åbne app
- **Spotlight-integration:** søg brands fra system-søgning

## Fase-plan

### V1 — Kerne-flow (3-4 uger på Mac mini)
- [ ] Repo oprettet: `SergentISAF/OrbisX-iOS` (eller `<brand>-iOS` når navnet er valgt)
- [ ] Xcode-projekt med App Group + Keychain entitlements
- [ ] Login/signup-skærm mod `/api/auth`
- [ ] Workspace-skærm med EntityCard-liste
- [ ] Entity-detalje med AVE + top historier + top medier
- [ ] Pull-to-refresh kalder `/api/entities/{id}/sync`
- [ ] Share-sheet til hurtig-rapport
- [ ] TestFlight build til Mikkel

### V2 — Vane-skabende (1-2 uger)
- [ ] Push-notifikationer (APNs server-side i FastAPI)
- [ ] Hjemmeskærms-widget (WidgetKit, viser top entity's AVE)
- [ ] Indstillinger-skærm (workspace, log ud, notifikations-tidspunkt)

### V3+ — Premium
- [ ] Apple Watch-app med komplikation
- [ ] Live Activity under aktiv kampagne
- [ ] App Clip til sponsor-rapport-deling

## Åbne afhængigheder

- **Brand-navn:** Glimt er taget. Søgte alternativer: glimva, klippora, klangra, bragra. Vælges før App Store-submission.
- **Apple Developer Account:** HolmstadIT-konto findes ([[apple-developer-account]]) — bruges
- **Backend public URL:** App skal kalde HTTPS-endpoint. Lige nu `https://elpris-dashboard.tail330027.ts.net`. Skal blive `https://app.holmstadit.dk` eller `https://api.<brand>.dk`
- **API-versionering:** Vores API har version 0.0.1. Skal låses så app ikke breaker ved backend-ændringer.

## Næste skridt (når du siger til)

1. Vælg brand-navn (eller acceptér midlertidigt arbejdsnavn til TestFlight)
2. Bekræft backend-URL er stabil (gerne `app.holmstadit.dk`)
3. Jeg opretter `<brand>-iOS` repo og bootstrap'er Xcode-projekt
4. Bygger workspace + entity-detalje først (det er 70% af V1-værdien)

## Relateret memory

- [[orbisx-morgendagens-vaerktoej]] — backend + web-dashboard projekt
- [[vaken-app]] — SwiftUI-stack reference (samme tech på Mac mini)
- [[mac-mini-claude-code-setup]] — Xcode + Claude Code setup på Mac mini
- [[apple-developer-account]] — HolmstadIT@icloud.com konto
