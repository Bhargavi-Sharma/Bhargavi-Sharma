# Job bot

Finds Data Engineer / Analytics Engineer / ETL / BI openings at product
companies that match your actual skills, and drafts a starting-point
cover note for each new match. **It does not submit applications for
you** — you still open the link and click apply yourself. See
[Why not fully automatic?](#why-not-fully-automatic) for the reasoning.

## What it does each run

1. Fetches current openings from the public job-board APIs of the
   companies in `config/companies.yaml` (Greenhouse, Lever, Ashby,
   SmartRecruiters — all unauthenticated, published by the vendors
   themselves for this purpose).
2. Filters to titles matching `config/profile.yaml`'s `target_titles`
   and drops senior/leadership roles via `exclude_title_keywords`.
3. Scores each remaining posting by weighted skill-keyword overlap
   (`skill_weights`) against your resume's actual tech stack, dropping
   anything under `min_score`.
4. For postings it hasn't seen before, writes a draft (`data/drafts/`)
   with a tailored cover-note starting point and your standard
   application answers.
5. Writes `data/reports/latest.html` and `latest.csv` with every current
   match, plus a "check manually" section of direct search links for
   big companies that don't expose a public job API (Google, Amazon,
   Microsoft, Flipkart, Swiggy, etc. — see below).
6. Emails a digest of new matches if SMTP is configured.

## Setup

```bash
cd job-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in SMTP creds if you want email, or skip
python -m src.main run
open data/reports/latest.html
```

Without `.env`/SMTP env vars set, it still runs fine — it just skips the
email step and tells you so. The report and drafts are written either way.

Run `python -m src.main run --dry-run` to skip email even if SMTP is
configured (useful while tuning `min_score`). Run with
`--min-score 4` to temporarily loosen the threshold for one run.

## Configuration

- **`config/profile.yaml`** — your skills, target titles, scoring
  weights, and the answers reused in drafts (notice period, work
  authorization, etc.). Update this as your resume changes. Once you
  get the AWS Data Engineer certification, add it under
  `certifications_in_progress` -> move it to a new `certifications`
  list (and mention "AWS Certified" as a skill keyword) so it shows up
  in scoring and drafts.
- **`config/companies.yaml`** — the company list. To add one: open its
  careers page, check the URL pattern (documented at the top of the
  file) to identify Greenhouse/Lever/Ashby/SmartRecruiters, then add an
  entry with its slug.

## Running it on a schedule

`.github/workflows/job-bot.yml` runs this daily via GitHub Actions
(free on a personal repo) and uploads the report/drafts as a downloadable
artifact each run. To enable email from Actions, add these as repo
secrets (Settings -> Secrets and variables -> Actions):

`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_TO`, `EMAIL_FROM`

For Gmail, `SMTP_PASS` must be an
[App Password](https://myaccount.google.com/apppasswords), not your
normal password. Seen-job state persists between runs via `actions/cache`
so you won't get re-notified about the same posting every day.

You can also just run `python -m src.main run` locally/via cron on your
own machine instead of using Actions.

## Why not fully automatic?

A bot that silently submits applications end-to-end was considered and
deliberately not built:

- Most ATS platforms (Workday, LinkedIn Easy Apply, Greenhouse's own
  apply flow) prohibit automated submissions in their terms of service;
  doing it anyway risks your account/profile getting flagged.
- Auto-filled, unreviewed applications tend to perform *worse* than
  ones you glance at first — wrong pronoun in a template, a skill you
  don't actually have gets pattern-matched in, an ATS-specific
  question left blank.
- Company career sites without a public job API (most "big name" ones —
  see `manual_check_links` in `companies.yaml`) use rendered pages, login
  walls, or CAPTCHAs that make reliable automated submission both
  fragile and much closer to the kind of bot activity these sites
  actively try to block.

What this gets you instead: the tedious part (finding + triaging
openings across dozens of company sites, remembering which ones you
already saw) is automated, and the two-minute part (final read-through,
click submit) stays yours.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests run against saved API-response fixtures in `tests/fixtures/` —
they don't hit the network, so they'll pass even in an environment with
no internet access.
