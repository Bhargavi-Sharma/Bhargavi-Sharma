"""Title filtering and weighted skill scoring against a candidate profile."""

import re
from dataclasses import dataclass, field


@dataclass
class MatchResult:
    job: dict
    score: int
    matched_skills: list[str] = field(default_factory=list)


def title_passes(title: str, profile: dict) -> bool:
    title_lower = title.lower()
    if not any(t.lower() in title_lower for t in profile["target_titles"]):
        return False
    if any(x.lower() in title_lower for x in profile.get("exclude_title_keywords", [])):
        return False
    return True


def description_disqualified(description: str, profile: dict) -> bool:
    """True if the description contains language ruling the candidate out
    outright (residency/citizenship/work-authorization restrictions) --
    caught by matching real postings against a candidate who needs visa
    sponsorship and found several "Remote - US" roles that were never
    actually reachable regardless of skill score."""
    patterns = profile.get("exclude_description_patterns", [])
    if not patterns or not description:
        return False
    return any(re.search(p, description, re.IGNORECASE) for p in patterns)


def score_job(job: dict, profile: dict) -> MatchResult | None:
    if not title_passes(job.get("title", ""), profile):
        return None

    if description_disqualified(job.get("description", ""), profile):
        return None

    haystack = f"{job.get('title', '')} {job.get('description', '')}".lower()
    weights = profile["skill_weights"]

    score = 0
    matched = []
    for skill, weight in weights.items():
        if skill.lower() in haystack:
            score += weight
            matched.append(skill)

    if score < profile.get("min_score", 0):
        return None

    return MatchResult(job=job, score=score, matched_skills=sorted(matched))


def score_jobs(jobs: list[dict], profile: dict) -> list[MatchResult]:
    results = []
    for job in jobs:
        result = score_job(job, profile)
        if result:
            results.append(result)
    results.sort(key=lambda r: r.score, reverse=True)
    return results
