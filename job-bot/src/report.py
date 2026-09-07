"""Builds the HTML and CSV reports written to data/reports/ each run."""

import csv
import io
from datetime import datetime, timezone
from html import escape

from .matcher import MatchResult

_STYLE = """
body { font-family: -apple-system, Segoe UI, Arial, sans-serif; max-width: 900px; margin: 2rem auto; color: #1a1a1a; }
h1 { font-size: 1.4rem; }
h2 { font-size: 1.1rem; margin-top: 2rem; border-bottom: 1px solid #ddd; padding-bottom: 0.25rem; }
table { border-collapse: collapse; width: 100%; margin-top: 0.5rem; }
th, td { text-align: left; padding: 0.5rem; border-bottom: 1px solid #eee; font-size: 0.9rem; vertical-align: top; }
th { background: #fafafa; }
.new { background: #eefbf0; }
.score { font-weight: 600; }
.skills { color: #555; font-size: 0.85rem; }
.manual a { display: inline-block; margin: 0.2rem 0.6rem 0.2rem 0; }
"""


def build_html_report(
    results: list[MatchResult], manual_check_links: list[dict], new_ids: set[str]
) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = []
    for r in results:
        job = r.job
        row_class = "new" if job["source_id"] in new_ids else ""
        rows.append(
            f"<tr class='{row_class}'>"
            f"<td>{escape(job['company'])}</td>"
            f"<td><a href='{escape(job['url'])}' target='_blank' rel='noopener'>{escape(job['title'])}</a></td>"
            f"<td>{escape(job.get('location') or '')}</td>"
            f"<td class='score'>{r.score}</td>"
            f"<td class='skills'>{escape(', '.join(r.matched_skills))}</td>"
            f"<td>{'NEW' if job['source_id'] in new_ids else ''}</td>"
            "</tr>"
        )

    manual_html = "".join(
        f"<a href='{escape(m['url'])}' target='_blank' rel='noopener'>{escape(m['name'])}</a>"
        for m in manual_check_links
    )

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Job matches — {generated}</title><style>{_STYLE}</style></head>
<body>
<h1>Job matches for Bhargavi Sharma</h1>
<p>Generated {generated}. {len(results)} matches across tracked companies, {len(new_ids)} new since last run.</p>

<h2>Automated matches (scored against your skills)</h2>
<table>
<tr><th>Company</th><th>Role</th><th>Location</th><th>Score</th><th>Matched skills</th><th></th></tr>
{''.join(rows) if rows else "<tr><td colspan='6'>No matches this run.</td></tr>"}
</table>

<h2>Check manually (no public job API to auto-score)</h2>
<p class="manual">{manual_html}</p>

</body></html>
"""


def build_csv(results: list[MatchResult]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["company", "title", "location", "score", "matched_skills", "url", "source_id"])
    for r in results:
        job = r.job
        writer.writerow(
            [
                job["company"],
                job["title"],
                job.get("location") or "",
                r.score,
                ", ".join(r.matched_skills),
                job["url"],
                job["source_id"],
            ]
        )
    return buf.getvalue()
