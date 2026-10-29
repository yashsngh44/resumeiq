from app.services.job_matcher import JobMatcher

def test_job_matcher_full_alignment():
    resume_text = """
    Software Engineer with deep experience in Python, Flask, React, and PostgreSQL.
    Architected REST APIs and managed data pipelines using SQL.
    Proficient in Git and Linux.
    """
    job_description = """
    Requirements:
    - Strong proficiency in Python and Flask
    - Experience building web applications using React
    - Familiarity with PostgreSQL databases

    Nice to have:
    - Docker containerization
    - AWS cloud deployment
    """
    result = JobMatcher.match(resume_text, job_description, ats_score=85.0)

    assert 0 <= result["job_match_score"] <= 100
    assert result["scoring_breakdown"] is not None

    matched_names = [s["skill"] for s in result["matched_skills"]]
    assert "Python" in matched_names
    assert "Flask" in matched_names
    assert "React" in matched_names
    assert "PostgreSQL" in matched_names

    # Check evidence quote presence
    python_match = next(s for s in result["matched_skills"] if s["skill"] == "Python")
    assert "evidence" in python_match and python_match["evidence"]

    # Check missing skills: Docker and AWS were not in resume
    missing_names = [s["skill"] for s in result["missing_skills"]]
    assert "Docker" in missing_names
    assert "AWS" in missing_names

def test_job_matcher_formula_exact_calculation():
    resume = "Candidate with Python and SQL experience."
    jd = "Requirements: Python. Preferred: SQL."
    result = JobMatcher.match(resume, jd, ats_score=80.0)

    breakdown = result["scoring_breakdown"]["sub_scores"]
    req = breakdown["required_skills_score"]
    pref = breakdown["preferred_skills_score"]
    exp = breakdown["experience_alignment_score"]
    ats = breakdown["ats_formatting_score"]

    expected_score = round((0.50 * req) + (0.25 * pref) + (0.15 * exp) + (0.10 * ats), 1)
    assert result["job_match_score"] == expected_score

def test_job_matcher_partial_family_match():
    # Candidate has Flask, JD asks for Django (both backend frameworks)
    resume = "Expert Python developer specializing in Flask microservices."
    jd = "Requirements: Django backend framework."
    result = JobMatcher.match(resume, jd, ats_score=75.0)

    # Should detect partial match via framework family
    partial_names = [s["skill"] for s in result["partial_skills"]]
    assert "Django" in partial_names
    django_item = next(s for s in result["partial_skills"] if s["skill"] == "Django")
    assert django_item["related_skill_found"] == "Flask"
