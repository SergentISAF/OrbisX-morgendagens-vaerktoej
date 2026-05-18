"""AVE (Advertising Value Equivalent) — annonceværdi-estimat per artikel.

Beregner hvad medieomtalen ville have kostet hvis det var købt som annonce.
Det er et grovt estimat baseret på outlet-tier og hvor længe artiklen lå på
forsiden (prominence-faktor).

Tallene er rough industry estimates — kunde bør kunne justere senere.
"""

from app.sources.orbisx import Article

# Grov DKK-værdi per artikel-omtale baseret på outlet-type
# Når vi har rigtige rate-cards per kunde, bliver disse erstattet
TIER_VALUES_DKK = {
    "national_broadcast": 30_000,    # DR, TV2
    "national_news": 25_000,         # Politiken, Berlingske, BT, JP
    "business": 15_000,              # Børsen, Finans, FoedevareWatch
    "regional_news": 8_000,          # JydskeVestkysten, nordjyske, Sjællandske
    "niche_blog": 4_000,             # Branche-sites, små blogs
    "unknown": 6_000,                # Fallback
}

# Outlet -> tier mapping. Udvides løbende.
OUTLET_TIERS: dict[str, str] = {
    # National broadcast
    "DR": "national_broadcast",
    "DR Nyheder": "national_broadcast",
    "TV2": "national_broadcast",
    "TV 2": "national_broadcast",
    "TV2 Nord": "national_broadcast",
    "TV2 Lorry": "national_broadcast",
    "TV2 Fyn": "national_broadcast",
    "TV2 Østjylland": "national_broadcast",
    # National news
    "Politiken": "national_news",
    "Berlingske": "national_news",
    "Jyllands-Posten": "national_news",
    "BT": "national_news",
    "Ekstra Bladet": "national_news",
    "Information": "national_news",
    "Weekendavisen": "national_news",
    # Business
    "Børsen": "business",
    "Finans": "business",
    "FoedevareWatch": "business",
    "ITWatch": "business",
    "FinansWatch": "business",
    "MediaWatch": "business",
    "MedWatch": "business",
    "Food Supply": "business",
    "EnergiWatch": "business",
    # Regional
    "JydskeVestkysten": "regional_news",
    "JV Sønderborg": "regional_news",
    "nordjyske": "regional_news",
    "Nordjyske": "regional_news",
    "Sjællandske Nyheder": "regional_news",
    "Fyens Stiftstidende": "regional_news",
    "Århus Stiftstidende": "regional_news",
    "Bornholms Tidende": "regional_news",
    # Sports niche
    "Hbold": "niche_blog",
    "Bold.dk": "niche_blog",
    "Tipsbladet": "niche_blog",
}


def tier_for_outlet(site_name: str) -> str:
    """Returner tier for en outlet. Fallback til 'unknown'."""
    return OUTLET_TIERS.get(site_name, "unknown")


def prominence_factor(time_on_frontpage_hours: int | None) -> float:
    """Multiplikator baseret på hvor længe artiklen lå på forsiden.

    0 timer = baseline (1.0). 24 timer = 2x. Klipset til max 3x.
    """
    if not time_on_frontpage_hours or time_on_frontpage_hours <= 0:
        return 1.0
    factor = 1.0 + time_on_frontpage_hours / 24.0
    return min(factor, 3.0)


def article_ave(article: Article) -> int:
    """AVE for én artikel i DKK (afrundet)."""
    tier = tier_for_outlet(article.site_name)
    base = TIER_VALUES_DKK[tier]
    factor = prominence_factor(article.time_on_frontpage)
    return int(round(base * factor))


def total_ave(articles: list[Article]) -> int:
    """Samlet AVE for en liste af artikler."""
    return sum(article_ave(a) for a in articles)


def ave_summary(articles: list[Article]) -> dict:
    """Returner total + breakdown per tier."""
    from collections import Counter

    tier_counts = Counter(tier_for_outlet(a.site_name) for a in articles)
    total = total_ave(articles)
    avg = total // len(articles) if articles else 0
    return {
        "total_dkk": total,
        "avg_per_article_dkk": avg,
        "sample_size": len(articles),
        "tier_distribution": dict(tier_counts),
    }
