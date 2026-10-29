import json
from app import db_session
from app.models.analysis import Analysis

def test_database_crud(app):
    report_dict = {
        "candidate_name": "Test User",
        "job_title": "Backend Dev",
        "matched_skills": [{"skill": "Python"}],
        "missing_skills": [{"skill": "Docker"}]
    }

    record = Analysis(
        candidate_name="Test User",
        resume_filename="test_resume.pdf",
        job_title="Backend Dev",
        company_name="Acme Inc",
        has_job_description=True,
        job_match_score=82.5,
        ats_readiness_score=88.0,
        is_demo_mode=True,
        model_used="heuristic-demo",
        summary="Test executive summary.",
        key_strengths=json.dumps(["Python API development"]),
        key_gaps=json.dumps(["Docker"]),
        full_report_json=json.dumps(report_dict)
    )

    db_session.add(record)
    db_session.commit()
    assert record.id is not None

    # Query back
    fetched = db_session.query(Analysis).filter_by(id=record.id).first()
    assert fetched is not None
    assert fetched.candidate_name == "Test User"
    assert fetched.job_match_score == 82.5

    summary = fetched.to_summary_dict()
    assert summary["candidate_name"] == "Test User"
    assert "Python API development" in summary["key_strengths"]

    full = fetched.to_full_dict()
    assert "report" in full
    assert full["report"]["candidate_name"] == "Test User"

    # Delete
    db_session.delete(fetched)
    db_session.commit()

    deleted = db_session.query(Analysis).filter_by(id=record.id).first()
    assert deleted is None
