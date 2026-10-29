from app.services.ats_checker import ATSChecker
from app.services.document_parser import DocumentParser

def test_ats_checker_complete_resume(sample_pdf_path):
    parsed = DocumentParser.parse_document(sample_pdf_path)
    ats_res = ATSChecker.evaluate(parsed)

    assert 0 <= ats_res["score"] <= 100
    assert ats_res["is_deterministic"] is True
    assert "disclaimer" in ats_res
    assert len(ats_res["checks"]) >= 5

    # Check that email and phone passed
    email_check = next(c for c in ats_res["checks"] if c["name"] == "Email Address")
    assert email_check["status"] == "passed"
    assert email_check["score"] == 10.0

def test_ats_checker_missing_contact():
    mock_parsed = {
        "raw_text": "Software Engineer with basic experience.",
        "contact_info": {"email": None, "phone": None, "linkedin": None, "github": None},
        "sections": {},
        "word_count": 50,
        "page_count": 1,
        "bullet_points": []
    }
    ats_res = ATSChecker.evaluate(mock_parsed)
    assert ats_res["score"] < 50
    assert ats_res["grade"] in ("Needs Improvement", "Critical Attention")
    
    email_check = next(c for c in ats_res["checks"] if c["name"] == "Email Address")
    assert email_check["status"] == "failed"
