"""Clients for public, unauthenticated ATS job-board JSON APIs.

Each fetch_* function returns a list of normalized job dicts:
    {source, source_id, company, title, location, url, description, posted_at}

These endpoints are published by the ATS vendors themselves for public
consumption (they back the vendors' own embeddable job widgets), so
fetching them on a reasonable schedule is not a ToS violation the way
scraping a logged-in site or a rendered career page would be. Still,
keep request volume modest and identify the client via User-Agent.
"""

import re

import requests

USER_AGENT = "job-bot/1.0 (personal job search tool; contact via resume email)"
TIMEOUT = 15

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(html: str) -> str:
    if not html:
        return ""
    text = _TAG_RE.sub(" ", html)
    return re.sub(r"\s+", " ", text).strip()


def _get(url: str, params: dict | None = None) -> dict | list | None:
    try:
        resp = requests.get(
            url, params=params, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT
        )
        if resp.status_code != 200:
            return None
        return resp.json()
    except requests.RequestException:
        return None


def fetch_greenhouse(company_name: str, slug: str) -> list[dict]:
    data = _get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", {"content": "true"})
    if not data:
        return []
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(
            {
                "source": "greenhouse",
                "source_id": f"greenhouse:{slug}:{j.get('id')}",
                "company": company_name,
                "title": j.get("title", ""),
                "location": (j.get("location") or {}).get("name", ""),
                "url": j.get("absolute_url", ""),
                "description": _strip_html(j.get("content", "")),
                "posted_at": j.get("updated_at"),
            }
        )
    return jobs


def fetch_lever(company_name: str, slug: str) -> list[dict]:
    data = _get(f"https://api.lever.co/v0/postings/{slug}", {"mode": "json"})
    if not data:
        return []
    jobs = []
    for j in data:
        categories = j.get("categories", {}) or {}
        jobs.append(
            {
                "source": "lever",
                "source_id": f"lever:{slug}:{j.get('id')}",
                "company": company_name,
                "title": j.get("text", ""),
                "location": categories.get("location", ""),
                "url": j.get("hostedUrl", ""),
                "description": j.get("descriptionPlain") or _strip_html(j.get("description", "")),
                "posted_at": j.get("createdAt"),
            }
        )
    return jobs


def fetch_ashby(company_name: str, slug: str) -> list[dict]:
    data = _get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
    if not data:
        return []
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(
            {
                "source": "ashby",
                "source_id": f"ashby:{slug}:{j.get('id')}",
                "company": company_name,
                "title": j.get("title", ""),
                "location": j.get("location", ""),
                "url": j.get("jobUrl", ""),
                "description": j.get("descriptionPlain") or _strip_html(j.get("descriptionHtml", "")),
                "posted_at": j.get("publishedAt"),
            }
        )
    return jobs


def fetch_smartrecruiters(company_name: str, slug: str) -> list[dict]:
    """List endpoint only -- no job description text available here.

    Descriptions are fetched per-posting on demand via
    enrich_smartrecruiters_description, called from main.py only for
    postings that already passed the title filter, to keep request
    volume down.
    """
    data = _get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings")
    if not data:
        return []
    jobs = []
    for j in data.get("content", []):
        location = j.get("location", {}) or {}
        loc_str = ", ".join(filter(None, [location.get("city"), location.get("country")]))
        jobs.append(
            {
                "source": "smartrecruiters",
                "source_id": f"smartrecruiters:{slug}:{j.get('id')}",
                "company": company_name,
                "title": j.get("name", ""),
                "location": loc_str,
                "url": j.get("ref", ""),
                "description": "",
                "posted_at": j.get("releasedDate"),
                "_slug": slug,
                "_posting_id": j.get("id"),
            }
        )
    return jobs


def enrich_smartrecruiters_description(slug: str, posting_id: str) -> str:
    data = _get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings/{posting_id}")
    if not data:
        return ""
    sections = (data.get("jobAd") or {}).get("sections") or {}
    parts = []
    for section in sections.values():
        text = section.get("text") if isinstance(section, dict) else None
        if text:
            parts.append(_strip_html(text))
    return " ".join(parts)


FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
    "smartrecruiters": fetch_smartrecruiters,
}


def fetch_all(companies: list[dict]) -> list[dict]:
    jobs = []
    for company in companies:
        fetcher = FETCHERS.get(company["ats"])
        if not fetcher:
            continue
        jobs.extend(fetcher(company["name"], company["slug"]))
    return jobs
