"""Generates a per-job markdown draft: a tailored cover-note starting
point plus your standard application answers, so applying is
copy/paste/tweak rather than starting from a blank page. This does not
submit anything -- you still open the job's apply link and do that
yourself.
"""

import re
from pathlib import Path

from .matcher import MatchResult

DEFAULT_DRAFTS_DIR = Path(__file__).resolve().parent.parent / "data" / "drafts"


def _slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:60] or "job"


def _cover_note(result: MatchResult, profile: dict) -> str:
    job = result.job
    contact = profile["contact"]
    weights = profile["skill_weights"]

    top_skills = sorted(result.matched_skills, key=lambda s: weights.get(s, 0), reverse=True)[:3]
    top_skills_str = ", ".join(top_skills) if top_skills else "your tech stack"
    matched_str = ", ".join(result.matched_skills) if result.matched_skills else "your tech stack"

    certs = profile.get("certifications_in_progress") or []
    cert_line = ""
    if certs:
        cert = certs[0]
        cert_line = f"I'm also completing the {cert['name']} (expected {cert['expected']}). "

    return (
        f"Dear {job['company']} Hiring Team,\n\n"
        f"I'm applying for the {job['title']} role. I'm a Data Engineer with "
        f"{profile['experience_years']}+ years of experience building cloud ETL pipelines and "
        f"BI reporting across AWS, GCP, and SQL Server, most recently at Accenture (client: "
        f"Navisite), where I re-engineered a legacy pipeline into a fully automated AWS Glue "
        f"and Step Functions workflow and cut a client-facing report's query runtime by 98%. "
        f"Your posting's emphasis on {top_skills_str} lines up directly with my hands-on work "
        f"in {matched_str}. {cert_line}\n\n"
        f"I'd welcome the chance to talk about how I can contribute to {job['company']}'s data team.\n\n"
        f"{contact['name']}\n"
        f"{contact['email']} | {contact['phone']} | {contact['linkedin']} | {contact['github']}\n"
    )


def build_draft(result: MatchResult, profile: dict) -> str:
    job = result.job
    answers = profile.get("standard_answers", {})

    lines = [
        f"# {job['title']} — {job['company']}",
        "",
        f"- Location: {job.get('location') or 'n/a'}",
        f"- Apply link: {job.get('url')}",
        f"- Match score: {result.score}",
        f"- Matched skills: {', '.join(result.matched_skills) or 'n/a'}",
        "",
        "## Draft cover note (edit before sending)",
        "",
        _cover_note(result, profile),
        "## Standard answers",
        "",
    ]
    if answers:
        for key, value in answers.items():
            label = key.replace("_", " ").title()
            lines.append(f"- **{label}:** {value or 'TODO'}")
    else:
        lines.append("_No standard_answers configured in config/profile.yaml._")

    lines += [
        "",
        "## Next step",
        "",
        f"Open the apply link above, attach your resume, paste/tailor the cover note, "
        f"answer the application's own questions using the standard answers as a reference, "
        f"and submit manually.",
        "",
    ]
    return "\n".join(lines)


def write_draft(result: MatchResult, profile: dict, drafts_dir: Path = DEFAULT_DRAFTS_DIR) -> Path:
    drafts_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{_slugify(result.job['company'])}-{_slugify(result.job['title'])}.md"
    path = drafts_dir / filename
    path.write_text(build_draft(result, profile), encoding="utf-8")
    return path
