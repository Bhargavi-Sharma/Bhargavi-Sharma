"""Tracks which job postings have already been reported, across runs.

Backed by a flat JSON file rather than a database -- this is a
single-user personal tool run at most a few times a day, so there is no
concurrency to worry about.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_STORE_PATH = Path(__file__).resolve().parent.parent / "data" / "seen_jobs.json"


class SeenStore:
    def __init__(self, path: Path = DEFAULT_STORE_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._seen: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def is_new(self, source_id: str) -> bool:
        return source_id not in self._seen

    def mark_seen(self, source_id: str) -> None:
        if source_id not in self._seen:
            self._seen[source_id] = datetime.now(timezone.utc).isoformat()

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._seen, f, indent=2, sort_keys=True)
