"""CLI entrypoint: fetch openings, score them against your profile, draft
new matches, write a report, and optionally email a digest.

Usage:
    python -m src.main run [--dry-run] [--min-score N]
    python -m src.main dump
"""

import argparse
import csv
import sys
from pathlib import Path

from . import fetchers
from .config import load_companies, load_profile
from .drafts import write_draft
from .matcher import score_jobs, title_passes
from .notifier import EmailNotConfigured, send_email_digest
from .report import build_csv, build_html_report
from .store import SeenStore

REPORTS_DIR = Path(__file__).resolve().parent.parent / "data" / "reports"


def run(dry_run: bool = False, min_score_override: int | None = None) -> int:
    profile = load_profile()
    companies_config = load_companies()

    if min_score_override is not None:
        profile["min_score"] = min_score_override

    print(f"Fetching openings from {len(companies_config['companies'])} companies...")
    jobs = fetchers.fetch_all(companies_config["companies"])
    print(f"Fetched {len(jobs)} total postings.")

    title_matched = [j for j in jobs if title_passes(j.get("title", ""), profile)]

    for job in title_matched:
        if job["source"] == "smartrecruiters" and not job.get("description") and job.get("_posting_id"):
            job["description"] = fetchers.enrich_smartrecruiters_description(
                job["_slug"], job["_posting_id"]
            )

    results = score_jobs(title_matched, profile)
    print(f"{len(results)} postings meet the min_score threshold ({profile['min_score']}).")

    store = SeenStore()
    new_ids = {r.job["source_id"] for r in results if store.is_new(r.job["source_id"])}

    for r in results:
        if r.job["source_id"] in new_ids:
            path = write_draft(r, profile)
            print(f"  NEW  [{r.score}] {r.job['company']} — {r.job['title']} -> {path}")
        store.mark_seen(r.job["source_id"])
    store.save()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    html = build_html_report(results, companies_config.get("manual_check_links", []), new_ids)
    csv_text = build_csv(results)
    (REPORTS_DIR / "latest.html").write_text(html, encoding="utf-8")
    (REPORTS_DIR / "latest.csv").write_text(csv_text, encoding="utf-8")
    print(f"Report written to {REPORTS_DIR / 'latest.html'}")

    if new_ids and not dry_run:
        try:
            send_email_digest(f"Job bot: {len(new_ids)} new matches", html)
            print(f"Emailed digest for {len(new_ids)} new matches.")
        except EmailNotConfigured as e:
            print(f"Skipping email ({e}). See job-bot/.env.example.")
    elif dry_run:
        print("Dry run: skipping email.")

    return 0


def dump() -> int:
    """Fetch every posting from every tracked company with no title/skill
    filtering, and write it to data/reports/raw_jobs.csv. This is for
    ad-hoc checks against a profile other than the one in
    config/profile.yaml (e.g. someone else's resume) without editing that
    file or committing anyone's personal data to the repo -- score the
    CSV against a throwaway profile wherever you're running this from.
    """
    companies_config = load_companies()
    print(f"Fetching openings from {len(companies_config['companies'])} companies...")
    jobs = fetchers.fetch_all(companies_config["companies"])
    print(f"Fetched {len(jobs)} total postings (unfiltered).")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / "raw_jobs.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["company", "title", "location", "url", "source_id", "description"])
        for job in jobs:
            writer.writerow(
                [
                    job["company"],
                    job["title"],
                    job.get("location") or "",
                    job["url"],
                    job["source_id"],
                    job.get("description") or "",
                ]
            )
    print(f"Raw postings written to {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Job matching bot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Fetch, match, draft, report, notify")
    run_parser.add_argument("--dry-run", action="store_true", help="Skip sending email")
    run_parser.add_argument("--min-score", type=int, default=None, help="Override profile min_score")

    subparsers.add_parser("dump", help="Fetch all postings unfiltered, for ad-hoc profile checks")

    args = parser.parse_args(argv)

    if args.command == "run":
        return run(dry_run=args.dry_run, min_score_override=args.min_score)
    if args.command == "dump":
        return dump()

    return 1


if __name__ == "__main__":
    sys.exit(main())
