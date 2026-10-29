from app.services.bullet_lab import BulletLab

def test_bullet_lab_passive_starter():
    original = "Responsible for building the user authentication service using Flask."
    result = BulletLab.analyze_and_improve(original, target_skills=["Flask"])

    assert "Responsible for" not in result["revised"]
    assert "Managed and executed" in result["revised"] or "Engineered" in result["revised"] or "Developed" in result["revised"]
    assert result["needs_user_metric"] is True
    assert result["user_metric_prompt"] is not None
    # Crucially verify no fake fabricated percentages like 'increased by 45%' are inserted without prompt
    assert "[Add your real metric" in result["revised"] or "metric" in result["revised"].lower()

def test_bullet_lab_preserves_existing_metric():
    original = "Optimized database queries, reducing latency by 40% across 50,000 queries."
    result = BulletLab.analyze_and_improve(original)

    assert result["needs_user_metric"] is False
    assert "40%" in result["revised"]
    assert "50,000" in result["revised"]

def test_bullet_lab_batch_generate():
    bullets = [
        {"id": "b1", "text": "Responsible for managing the MySQL database backup routines."},
        {"id": "b2", "text": "Worked on frontend React components for customer billing."},
        {"id": "b3", "text": "Short"}
    ]
    suggestions = BulletLab.batch_generate(bullets, ["React", "MySQL"])
    assert len(suggestions) == 2  # Short one filtered out
    assert suggestions[0]["id"] == "b1"
    assert suggestions[1]["id"] == "b2"
