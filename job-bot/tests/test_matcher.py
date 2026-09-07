from src.matcher import score_job, score_jobs, title_passes

PROFILE = {
    "target_titles": ["data engineer", "analytics engineer", "cloud data engineer"],
    "exclude_title_keywords": ["director", "staff", "principal", "architect"],
    "skill_weights": {
        "aws": 3,
        "glue": 3,
        "redshift": 3,
        "airflow": 3,
        "sql": 3,
        "python": 3,
        "bigquery": 2,
        "power bi": 2,
    },
    "min_score": 6,
}


def test_title_passes_matches_target():
    assert title_passes("Senior Data Engineer", PROFILE) is True


def test_title_passes_rejects_non_target():
    assert title_passes("Sales Engineer", PROFILE) is False


def test_title_passes_rejects_excluded_seniority():
    assert title_passes("Director of Data Engineering", PROFILE) is False


def test_title_passes_rejects_solutions_architect_false_positive():
    # "Data Engineering" contains the substring "data engineer", so this
    # would otherwise wrongly match despite being an Architect-level role.
    assert title_passes("Specialist Solutions Architect - Data Engineering", PROFILE) is False


def test_score_job_above_threshold():
    job = {
        "title": "Data Engineer II",
        "description": "Build pipelines with AWS Glue, Redshift, Airflow, SQL, and Python.",
        "company": "Acme",
    }
    result = score_job(job, PROFILE)
    assert result is not None
    assert result.score == 3 + 3 + 3 + 3 + 3 + 3  # aws, glue, redshift, airflow, sql, python
    assert set(result.matched_skills) == {"aws", "glue", "redshift", "airflow", "sql", "python"}


def test_score_job_below_threshold_returns_none():
    job = {
        "title": "Data Engineer",
        "description": "We use BigQuery and Power BI occasionally.",
        "company": "Acme",
    }
    assert score_job(job, PROFILE) is None  # 2 + 2 = 4 < min_score 6


def test_score_job_wrong_title_returns_none():
    job = {"title": "Sales Engineer", "description": "AWS Glue Redshift Airflow SQL Python", "company": "Acme"}
    assert score_job(job, PROFILE) is None


def test_score_jobs_sorted_descending():
    jobs = [
        {"title": "Data Engineer", "description": "BigQuery Power BI", "company": "A"},
        {"title": "Data Engineer", "description": "AWS Glue Redshift Airflow SQL Python", "company": "B"},
    ]
    results = score_jobs(jobs, PROFILE)
    assert len(results) == 1  # A scores 2+2=4, below the min_score 6 threshold
    assert results[0].job["company"] == "B"
