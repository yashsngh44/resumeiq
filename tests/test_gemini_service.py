import json
from unittest.mock import MagicMock, patch
import pytest
from app.services.gemini_service import GeminiService, GeminiServiceError, GeminiAnalysisSchema

def test_gemini_schema_validation():
    valid_data = {
        "summary": "Candidate demonstrates strong full stack development capabilities.",
        "strengths": ["Solid Python foundation", "Experience with Docker"],
        "weaknesses": ["Needs more quantitative project metrics"],
        "matched_skills": [
            {
                "skill": "Python",
                "category": "Languages",
                "type": "Required",
                "evidence": "Developed backend in Python",
                "explanation": "Direct match"
            }
        ],
        "partial_matches": [],
        "missing_or_unverified_skills": [],
        "bullet_improvements": [],
        "recommendations": ["Add GitHub link"],
        "limitations": ["Automated assessment"]
    }
    schema = GeminiAnalysisSchema(**valid_data)
    assert schema.summary == valid_data["summary"]
    assert len(schema.matched_skills) == 1
    assert schema.matched_skills[0].skill == "Python"

def test_gemini_service_demo_fallback():
    # Empty API key should immediately invoke SyntheticEngine without network request
    svc = GeminiService(api_key="", model_name="gemini-2.5-flash")
    assert svc.is_available() is False

    mock_doc = {
        "candidate_name": "Test Candidate",
        "raw_text": "Experienced Python and SQL engineer with Flask experience.",
        "contact_info": {"email": "test@example.com", "phone": "555-1234"},
        "sections": {"experience": "Worked with Python and Flask", "skills": "Python, SQL"},
        "bullet_points": [{"id": "b1", "text": "Responsible for building Python APIs"}]
    }

    result = svc.analyze_resume(mock_doc, job_description="Looking for Python and Docker", force_demo=True)
    assert result["is_demo_mode"] is True
    assert "Academic Heuristic Engine" in result["model_used"]
    assert result["ats_readiness_score"] > 0
    assert result["job_match_score"] is not None

@patch.object(GeminiService, "_call_gemini_api")
def test_gemini_service_mocked_success(mock_call):
    mock_json_response = json.dumps({
        "summary": "Mocked AI assessment for candidate.",
        "strengths": ["Excellent API design background"],
        "weaknesses": ["Limited Kubernetes cloud experience"],
        "matched_skills": [
            {
                "skill": "Python",
                "category": "Languages",
                "type": "Required",
                "evidence": "3 years Python experience",
                "explanation": "Direct match"
            }
        ],
        "partial_matches": [],
        "missing_or_unverified_skills": [
            {
                "skill": "Docker",
                "category": "Cloud & DevOps",
                "type": "Required",
                "explanation": "No written evidence in resume."
            }
        ],
        "bullet_improvements": [
            {
                "original": "Worked on web app.",
                "revised": "Architected web application serving 10K users.",
                "weakness_identified": "Passive starter",
                "what_changed": "Action verb",
                "job_requirement_supported": "Python",
                "needs_user_metric": False,
                "user_metric_prompt": None
            }
        ],
        "recommendations": ["Practice containerization with Docker"],
        "limitations": ["Mock test"]
    })
    mock_call.return_value = mock_json_response

    svc = GeminiService(api_key="valid_dummy_key_12345", model_name="gemini-2.5-flash")
    mock_doc = {
        "candidate_name": "Jane Doe",
        "raw_text": "Jane Doe. Email: jane@example.com. Python developer with 3 years experience.",
        "contact_info": {"email": "jane@example.com", "phone": "555-4321"},
        "sections": {"experience": "Python developer", "skills": "Python"},
        "bullet_points": [{"id": "b1", "text": "Worked on web app."}]
    }

    report = svc.analyze_resume(mock_doc, job_description="Requirements: Python and Docker", force_demo=False)
    assert report["is_demo_mode"] is False
    assert "gemini-2.5-flash" in report["model_used"]
    assert report["summary"] == "Mocked AI assessment for candidate."
    assert len(report["matched_skills"]) == 1
    assert len(report["missing_skills"]) == 1
    assert len(report["roadmap"]) >= 1  # Roadmap generated from missing Docker
