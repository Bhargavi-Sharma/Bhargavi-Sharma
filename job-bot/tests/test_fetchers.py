import json
from pathlib import Path

from src import fetchers

FIXTURES = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


def _load(name):
    with open(FIXTURES / name, encoding="utf-8") as f:
        return json.load(f)


def test_fetch_greenhouse(monkeypatch):
    monkeypatch.setattr(
        fetchers.requests, "get", lambda *a, **k: FakeResponse(_load("greenhouse_sample.json"))
    )
    jobs = fetchers.fetch_greenhouse("Acme", "acme")
    assert len(jobs) == 2
    assert jobs[0]["source"] == "greenhouse"
    assert jobs[0]["title"] == "Data Engineer II"
    assert "AWS Glue" in jobs[0]["description"]
    assert "<p>" not in jobs[0]["description"]
    assert jobs[0]["source_id"] == "greenhouse:acme:1001"


def test_fetch_lever(monkeypatch):
    monkeypatch.setattr(
        fetchers.requests, "get", lambda *a, **k: FakeResponse(_load("lever_sample.json"))
    )
    jobs = fetchers.fetch_lever("Acme", "acme")
    assert len(jobs) == 2
    assert jobs[0]["title"] == "Analytics Engineer"
    assert jobs[0]["location"] == "Remote"


def test_fetch_ashby(monkeypatch):
    monkeypatch.setattr(
        fetchers.requests, "get", lambda *a, **k: FakeResponse(_load("ashby_sample.json"))
    )
    jobs = fetchers.fetch_ashby("Acme", "acme")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Cloud Data Engineer"
    assert "Redshift" in jobs[0]["description"]


def test_fetch_smartrecruiters_list_only(monkeypatch):
    monkeypatch.setattr(
        fetchers.requests, "get", lambda *a, **k: FakeResponse(_load("smartrecruiters_sample.json"))
    )
    jobs = fetchers.fetch_smartrecruiters("Acme", "acme")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Data Engineer"
    assert jobs[0]["description"] == ""
    assert jobs[0]["_posting_id"] == "sr-1"


def test_enrich_smartrecruiters_description(monkeypatch):
    monkeypatch.setattr(
        fetchers.requests,
        "get",
        lambda *a, **k: FakeResponse(_load("smartrecruiters_detail_sample.json")),
    )
    description = fetchers.enrich_smartrecruiters_description("acme", "sr-1")
    assert "AWS Glue" in description
    assert "data warehousing" in description


def test_fetch_returns_empty_on_failure(monkeypatch):
    monkeypatch.setattr(fetchers.requests, "get", lambda *a, **k: FakeResponse(None, status_code=404))
    assert fetchers.fetch_greenhouse("Acme", "missing") == []
