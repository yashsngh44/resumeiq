import io
import json
from app import db_session
from app.models.analysis import Analysis

def test_page_routes(client):
    routes = ["/", "/dashboard", "/history", "/compare", "/settings"]
    for r in routes:
        resp = client.get(r)
        assert resp.status_code == 200, f"Route {r} failed with status {resp.status_code}"

def test_api_settings_status(client):
    resp = client.get("/api/settings/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "model_name" in data

def test_api_bullet_custom_improve(client):
    resp = client.post("/api/bullet/custom-improve", json={
        "bullet_text": "Responsible for managing the team database and wrote queries in SQL."
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "revised" in data["suggestion"]
    assert "Responsible for" not in data["suggestion"]["revised"]

def test_api_analyze_with_sample_pdf(client, sample_pdf_path):
    with open(sample_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    data = {
        "resume": (io.BytesIO(pdf_bytes), "alex_chen_fullstack.pdf"),
        "job_title": "Full Stack Engineer",
        "company_name": "Nexus Corp",
        "job_description": "We need an engineer experienced with Python, React, and PostgreSQL. Docker preferred.",
        "demo_mode": "true"
    }

    resp = client.post("/api/analyze", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data["success"] is True
    assert "analysis_id" in json_data
    analysis_id = json_data["analysis_id"]

    # Verify report page for created analysis
    report_page = client.get(f"/report/{analysis_id}")
    assert report_page.status_code == 200
    assert b"Alex Chen" in report_page.data

    # Verify export markdown
    export_resp = client.get(f"/api/export/{analysis_id}/markdown")
    assert export_resp.status_code == 200
    assert b"# ResumeIQ Analysis Report" in export_resp.data

def test_api_analyze_missing_file_error(client):
    resp = client.post("/api/analyze", data={}, content_type="multipart/form-data")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    assert "No resume file" in data["error"]

def test_api_compare_two_analyses(client):
    # Create two records in DB
    rec1 = Analysis(
        candidate_name="Alice",
        resume_filename="resume.pdf",
        job_title="Job 1",
        company_name="Company 1",
        has_job_description=True,
        job_match_score=75.0,
        ats_readiness_score=80.0,
        is_demo_mode=True,
        model_used="demo",
        summary="Summary 1",
        full_report_json=json.dumps({
            "matched_skills": [{"skill": "Python"}, {"skill": "Flask"}],
            "missing_skills": [{"skill": "Docker"}]
        })
    )
    rec2 = Analysis(
        candidate_name="Alice",
        resume_filename="resume.pdf",
        job_title="Job 2",
        company_name="Company 2",
        has_job_description=True,
        job_match_score=85.0,
        ats_readiness_score=80.0,
        is_demo_mode=True,
        model_used="demo",
        summary="Summary 2",
        full_report_json=json.dumps({
            "matched_skills": [{"skill": "Python"}, {"skill": "React"}],
            "missing_skills": [{"skill": "Kubernetes"}]
        })
    )
    db_session.add(rec1)
    db_session.add(rec2)
    db_session.commit()

    resp = client.post("/api/compare", json={"id1": rec1.id, "id2": rec2.id})
    assert resp.status_code == 200
    comp_data = resp.get_json()
    assert comp_data["success"] is True
    comp = comp_data["comparison"]
    assert "Python" in comp["shared_matched_skills"]
    assert comp["score_diff"] == 10.0
