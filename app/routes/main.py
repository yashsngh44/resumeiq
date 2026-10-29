from pathlib import Path
from flask import Blueprint, render_template, abort, send_from_directory
from .. import db_session
from ..models.analysis import Analysis

main_bp = Blueprint("main", __name__)

@main_bp.route("/sample_resumes/<path:filename>")
def serve_sample_resume(filename):
    """Serves test sample resumes for convenient testing."""
    sample_dir = Path(__file__).resolve().parent.parent.parent / "sample_resumes"
    return send_from_directory(str(sample_dir), filename)

@main_bp.route("/")
def index():
    """Landing page showcasing product differentiation and features."""
    return render_template("index.html")

@main_bp.route("/dashboard")
def dashboard():
    """Main application workspace: file upload and job description form."""
    return render_template("dashboard.html")

@main_bp.route("/report/<int:analysis_id>")
def report(analysis_id):
    """Detailed analysis report view."""
    record = db_session.query(Analysis).filter_by(id=analysis_id).first()
    if not record:
        abort(404)
    return render_template("report.html", analysis_id=analysis_id, analysis=record.to_full_dict())

@main_bp.route("/lab/<int:analysis_id>")
def lab(analysis_id):
    """Resume improvement lab view."""
    record = db_session.query(Analysis).filter_by(id=analysis_id).first()
    if not record:
        abort(404)
    return render_template("lab.html", analysis_id=analysis_id, analysis=record.to_full_dict())

@main_bp.route("/roadmap/<int:analysis_id>")
def roadmap(analysis_id):
    """Actionable career roadmap view."""
    record = db_session.query(Analysis).filter_by(id=analysis_id).first()
    if not record:
        abort(404)
    return render_template("roadmap.html", analysis_id=analysis_id, analysis=record.to_full_dict())

@main_bp.route("/history")
def history():
    """History of previous analyses with deletion and comparison tools."""
    return render_template("history.html")

@main_bp.route("/compare")
def compare():
    """Side-by-side comparison between two analyses."""
    return render_template("comparison.html")

@main_bp.route("/settings")
def settings():
    """Settings, Gemini API key configuration, and privacy information."""
    return render_template("settings.html")
