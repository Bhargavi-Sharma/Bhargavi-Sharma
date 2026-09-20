from src.drafts import build_draft, write_draft
from src.matcher import MatchResult

PROFILE = {
    "contact": {
        "name": "Test Person",
        "first_name": "Test",
        "last_name": "Person",
        "email": "test@example.com",
        "phone": "+1-555-0100",
        "linkedin": "linkedin.com/in/testperson",
        "github": "github.com/testperson",
        "location": "Nowhere",
        "address": "1 Main St, Nowhere",
        "pincode": "00000",
    },
    "experience_years": 2,
    "skill_weights": {"aws": 3, "sql": 3},
    "standard_answers": {"notice_period": "30 days"},
}


def _result(company, title, source_id, location="Remote"):
    job = {
        "company": company,
        "title": title,
        "location": location,
        "url": f"https://example.com/{source_id}",
        "source_id": source_id,
    }
    return MatchResult(job=job, score=10, matched_skills=["aws", "sql"])


def test_build_draft_includes_personal_info():
    draft = build_draft(_result("Acme", "Data Engineer", "greenhouse:acme:1"), PROFILE)
    assert "**First name:** Test" in draft
    assert "**Address:** 1 Main St, Nowhere" in draft
    assert "**Pincode / ZIP:** 00000" in draft


def test_write_draft_does_not_collide_across_locations(tmp_path):
    # Same company+title posted for two different locations (two distinct
    # source_ids) must not silently overwrite each other's file/apply link.
    us = _result("Acme", "Senior Data Engineer", "greenhouse:acme:100", location="Remote - US")
    canada = _result("Acme", "Senior Data Engineer", "greenhouse:acme:200", location="Remote - Canada")

    us_path = write_draft(us, PROFILE, drafts_dir=tmp_path)
    canada_path = write_draft(canada, PROFILE, drafts_dir=tmp_path)

    assert us_path != canada_path
    assert us_path.exists() and canada_path.exists()
    assert "greenhouse:acme:100" not in canada_path.read_text()
    assert "greenhouse:acme:100" in us_path.read_text()
    assert "greenhouse:acme:200" in canada_path.read_text()
