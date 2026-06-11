"""Finds new sponsorship candidate companies using web search."""

import re
import random
from duckduckgo_search import DDGS

from sponsor_bot.config import SEARCH_CATEGORIES, COMPANIES_PER_DAY
from sponsor_bot.companies_db import is_already_contacted


# Known email patterns by domain suffix / brand patterns
_EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# Common sponsorship / partnership contact email patterns to try
_CONTACT_PREFIXES = [
    "partnerships", "marketing", "sponsorship", "sponsor",
    "info", "contact", "hello", "press", "media",
]


def _extract_domain(url: str) -> str:
    url = re.sub(r"https?://", "", url)
    url = url.split("/")[0].split("?")[0]
    url = re.sub(r"^www\.", "", url)
    return url.lower()


def _guess_email(domain: str, prefix: str = "info") -> str:
    return f"{prefix}@{domain}"


def _search_companies(query: str, max_results: int = 20) -> list[dict]:
    """Search DuckDuckGo and extract company leads."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get("title", "").strip()
                url = r.get("href", "")
                body = r.get("body", "")

                if not url or not title:
                    continue

                domain = _extract_domain(url)
                # Skip non-brand domains
                if any(skip in domain for skip in [
                    "wikipedia", "reddit", "youtube", "instagram", "facebook",
                    "twitter", "linkedin", "amazon", "ebay", "etsy",
                    "quora", "medium", "blogspot", "wordpress",
                ]):
                    continue

                # Try to find an email in the snippet
                emails_found = _EMAIL_REGEX.findall(body)
                email = emails_found[0] if emails_found else _guess_email(domain, "info")

                # Detect language hint (Spanish keywords → es)
                language = "es" if any(w in (title + body).lower() for w in [
                    "empresa", "compañía", "patrocinio", "argentina", "latinoamerica",
                    "españa", "mexico", "brasil"
                ]) else "en"

                results.append({
                    "company": title[:80],
                    "domain": domain,
                    "email": email,
                    "language": language,
                    "category": _category_from_query(query),
                    "source_url": url,
                })
    except Exception as e:
        print(f"[WARN] Search failed for '{query}': {e}")
    return results


def _category_from_query(query: str) -> str:
    q = query.lower()
    if "karting" in q or "kart" in q:
        return "karting"
    if "energy" in q or "drink" in q or "nutrition" in q:
        return "energy_nutrition"
    if "gaming" in q or "sim racing" in q or "esports" in q:
        return "gaming_tech"
    if "automotive" in q or "tire" in q or "oil" in q:
        return "automotive"
    if "apparel" in q or "suit" in q or "helmet" in q or "gear" in q:
        return "motorsport_apparel"
    if "argentina" in q or "marca" in q or "empresa" in q:
        return "latin_america"
    if "fintech" in q or "crypto" in q:
        return "fintech"
    return "general"


def find_new_companies(db: dict, target: int = COMPANIES_PER_DAY) -> list[dict]:
    """Find up to `target` new (not yet contacted) companies."""
    categories = SEARCH_CATEGORIES.copy()
    random.shuffle(categories)

    candidates: list[dict] = []
    seen_domains: set[str] = set()

    for query in categories:
        if len(candidates) >= target * 2:
            break
        raw = _search_companies(query, max_results=15)
        for c in raw:
            domain = c["domain"]
            if domain in seen_domains:
                continue
            if is_already_contacted(db, c["email"], c["company"]):
                continue
            seen_domains.add(domain)
            candidates.append(c)

    # Deduplicate by domain and trim to target
    unique: list[dict] = []
    final_domains: set[str] = set()
    for c in candidates:
        if c["domain"] not in final_domains:
            final_domains.add(c["domain"])
            unique.append(c)
        if len(unique) >= target:
            break

    return unique
