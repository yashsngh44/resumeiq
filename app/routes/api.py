import os
import json
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, session, Response
from werkzeug.utils import secure_filename

from .. import db_session
from ..config import Config
from ..models.analysis import Analysis
from ..services.document_parser import DocumentParser, DocumentParsingError
from ..services.gemini_service import GeminiService, GeminiServiceError
from ..services.bullet_lab import BulletLab

api_bp = Blueprint("api", __name__)

@api_bp.route("/analyze", methods=["POST"])
def analyze():
    """
    Primary analysis endpoint:
    Processes uploaded PDF/DOCX file and optional job description.
    Runs deterministic parsers and Gemini AI (or Heuristic Demo Mode).
    Safely deletes temporary uploaded files immediately after text extraction.
    """
    if "resume" not in request.files:
        return jsonify({"success": False, "error": "No resume file provided in upload."}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    job_description = request.form.get("job_description", "").strip()
    job_title = request.form.get("job_title", "").strip()
    company_name = request.form.get("company_name", "").strip()
    force_demo = request.form.get("demo_mode", "false").lower() in ("true", "1", "yes")

    # Secure temporary file storage
    raw_filename = secure_filename(file.filename)
    extension = Path(raw_filename).suffix.lower()
    if extension not in (f".{ext}" for ext in Config.ALLOWED_EXTENSIONS):
        return jsonify({
            "success": False,
            "error": f"Unsupported format '{extension}'. Please upload a PDF (.pdf) or Word document (.docx)."
        }), 400

    unique_filename = f"{uuid.uuid4().hex}_{raw_filename}"
    temp_filepath = Path(Config.UPLOAD_FOLDER) / unique_filename

    try:
        file.save(str(temp_filepath))

        # 1. Document Parsing & Structure Detection
        parsed_doc = DocumentParser.parse_document(str(temp_filepath))

    except DocumentParsingError as dpe:
        return jsonify({"success": False, "error": str(dpe)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to process document: {str(e)}"}), 500
    finally:
        # Guarantee removal of temporary uploaded file from local filesystem
        if temp_filepath.exists():
            try:
                temp_filepath.unlink()
            except Exception:
                pass

    # 2. AI or Heuristic Analysis Execution
    api_key_override = session.get("custom_gemini_api_key") or Config.GEMINI_API_KEY
    gemini_svc = GeminiService(api_key=api_key_override, model_name=Config.GEMINI_MODEL)

    try:
        report_data = gemini_svc.analyze_resume(
            parsed_doc=parsed_doc,
            job_description=job_description,
            job_title=job_title,
            company_name=company_name,
            force_demo=force_demo
        )
    except GeminiServiceError as gse:
        return jsonify({
            "success": False,
            "error": gse.message,
            "can_retry": gse.can_retry,
            "can_fallback_demo": True
        }), gse.status_code
    except Exception as ex:
        return jsonify({
            "success": False,
            "error": f"Analysis pipeline error: {str(ex)}",
            "can_fallback_demo": True
        }), 500

    # 3. Persist Analysis Record into SQLite Database
    key_strengths = [s for s in report_data.get("strengths", [])[:4]]
    key_gaps = [m.get("skill", "") for m in report_data.get("missing_skills", [])[:4]]

    record = Analysis(
        candidate_name=report_data.get("candidate_name", "Candidate"),
        resume_filename=raw_filename,
        job_title=job_title or ("General Assessment" if not job_description else "Target Role"),
        company_name=company_name or "N/A",
        has_job_description=bool(job_description),
        job_match_score=report_data.get("job_match_score"),
        ats_readiness_score=report_data.get("ats_readiness_score", 0.0),
        is_demo_mode=report_data.get("is_demo_mode", False),
        model_used=report_data.get("model_used", "offline"),
        summary=report_data.get("summary", ""),
        key_strengths=json.dumps(key_strengths),
        key_gaps=json.dumps(key_gaps),
        full_report_json=json.dumps(report_data)
    )

    db_session.add(record)
    db_session.commit()

    return jsonify({
        "success": True,
        "analysis_id": record.id,
        "redirect_url": f"/report/{record.id}",
        "data": record.to_full_dict()
    })

@api_bp.route("/analyses", methods=["GET"])
def get_analyses():
    """Returns saved analysis summaries for history view."""
    records = db_session.query(Analysis).order_by(Analysis.created_at.desc()).all()
    return jsonify({
        "success": True,
        "analyses": [r.to_summary_dict() for r in records]
    })

@api_bp.route("/analyses/<int:analysis_id>", methods=["GET"])
def get_analysis_detail(analysis_id):
    """Retrieves full analysis report payload."""
    record = db_session.query(Analysis).filter_by(id=analysis_id).first()
    if not record:
        return jsonify({"success": False, "error": "Analysis record not found."}), 404
    return jsonify({"success": True, "analysis": record.to_full_dict()})

@api_bp.route("/analyses/<int:analysis_id>", methods=["DELETE"])
def delete_analysis(analysis_id):
    """Permanently deletes an individual analysis record and associated metadata."""
    record = db_session.query(Analysis).filter_by(id=analysis_id).first()
    if not record:
        return jsonify({"success": False, "error": "Record not found."}), 404

    db_session.delete(record)
    db_session.commit()
    return jsonify({"success": True, "message": f"Analysis #{analysis_id} deleted successfully."})

@api_bp.route("/analyses/all", methods=["DELETE"])
def delete_all_analyses():
    """Complete data deletion workflow: clears all saved analyses from SQLite database."""
    count = db_session.query(Analysis).delete()
    db_session.commit()
    return jsonify({"success": True, "message": f"All {count} analysis records removed permanently."})

@api_bp.route("/compare", methods=["POST"])
def compare_analyses():
    """
    Compares two analyses of the same resume against different job descriptions.
    Highlights requirement differences, shared strengths, and distinct gaps.
    """
    payload = request.get_json(silent=True) or {}
    id1 = payload.get("id1")
    id2 = payload.get("id2")

    if not id1 or not id2:
        return jsonify({"success": False, "error": "Please provide both analysis IDs to compare."}), 400

    rec1 = db_session.query(Analysis).filter_by(id=id1).first()
    rec2 = db_session.query(Analysis).filter_by(id=id2).first()

    if not rec1 or not rec2:
        return jsonify({"success": False, "error": "One or both analysis records were not found."}), 404

    dict1 = rec1.to_full_dict()
    dict2 = rec2.to_full_dict()

    rep1 = dict1.get("report", {})
    rep2 = dict2.get("report", {})

    skills1_matched = {s["skill"].lower(): s["skill"] for s in rep1.get("matched_skills", [])}
    skills2_matched = {s["skill"].lower(): s["skill"] for s in rep2.get("matched_skills", [])}

    skills1_missing = {s["skill"].lower(): s["skill"] for s in rep1.get("missing_skills", [])}
    skills2_missing = {s["skill"].lower(): s["skill"] for s in rep2.get("missing_skills", [])}

    # Set operations
    shared_matched = [skills1_matched[k] for k in skills1_matched if k in skills2_matched]
    only_in_job1_matched = [skills1_matched[k] for k in skills1_matched if k not in skills2_matched]
    only_in_job2_matched = [skills2_matched[k] for k in skills2_matched if k not in skills1_matched]

    shared_gaps = [skills1_missing[k] for k in skills1_missing if k in skills2_missing]
    only_in_job1_gaps = [skills1_missing[k] for k in skills1_missing if k not in skills2_missing]
    only_in_job2_gaps = [skills2_missing[k] for k in skills2_missing if k not in skills1_missing]

    score1 = rec1.job_match_score if rec1.job_match_score is not None else 0.0
    score2 = rec2.job_match_score if rec2.job_match_score is not None else 0.0
    score_diff = round(score2 - score1, 1)

    return jsonify({
        "success": True,
        "comparison": {
            "analysis1": {
                "id": rec1.id,
                "job_title": rec1.job_title,
                "company_name": rec1.company_name,
                "job_match_score": rec1.job_match_score,
                "ats_score": rec1.ats_readiness_score,
                "date": dict1["created_at"]
            },
            "analysis2": {
                "id": rec2.id,
                "job_title": rec2.job_title,
                "company_name": rec2.company_name,
                "job_match_score": rec2.job_match_score,
                "ats_score": rec2.ats_readiness_score,
                "date": dict2["created_at"]
            },
            "score_diff": score_diff,
            "shared_matched_skills": shared_matched,
            "job1_unique_matched": only_in_job1_matched,
            "job2_unique_matched": only_in_job2_matched,
            "shared_gaps": shared_gaps,
            "job1_unique_gaps": only_in_job1_gaps,
            "job2_unique_gaps": only_in_job2_gaps,
            "disclaimer": (
                "Academic Disclaimer: Score differences reflect text and keyword alignment variations between the two "
                "job descriptions, not an increased hiring probability."
            )
        }
    })

@api_bp.route("/bullet/update", methods=["POST"])
def update_bullet():
    """Updates user interaction state (accept, reject, edit) on a bullet rewrite suggestion."""
    payload = request.get_json(silent=True) or {}
    analysis_id = payload.get("analysis_id")
    bullet_id = payload.get("bullet_id")
    status = payload.get("status")  # "accepted", "rejected", "edited"
    user_edited_text = payload.get("user_edited_text")

    if not analysis_id or not bullet_id or not status:
        return jsonify({"success": False, "error": "Missing required fields."}), 400

    record = db_session.query(Analysis).filter_by(id=analysis_id).first()
    if not record:
        return jsonify({"success": False, "error": "Analysis not found."}), 404

    try:
        data = json.loads(record.full_report_json)
        bullets = data.get("bullet_improvements", [])
        updated = False

        for b in bullets:
            if b.get("id") == bullet_id:
                b["status"] = status
                if user_edited_text:
                    b["user_edited_text"] = user_edited_text
                updated = True
                break

        if updated:
            record.full_report_json = json.dumps(data)
            db_session.commit()
            return jsonify({"success": True, "message": "Bullet state updated successfully."})
        else:
            return jsonify({"success": False, "error": "Bullet ID not found in report."}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route("/bullet/custom-improve", methods=["POST"])
def custom_improve_bullet():
    """Generates an immediate XYZ revision for any user-provided bullet string."""
    payload = request.get_json(silent=True) or {}
    bullet_text = payload.get("bullet_text", "").strip()
    target_skills = payload.get("target_skills", [])

    if not bullet_text:
        return jsonify({"success": False, "error": "Please provide a bullet point string."}), 400

    improved = BulletLab.analyze_and_improve(bullet_text, target_skills)
    return jsonify({"success": True, "suggestion": improved})

@api_bp.route("/settings/status", methods=["GET"])
def settings_status():
    """Returns runtime configuration status."""
    active_key = session.get("custom_gemini_api_key") or Config.GEMINI_API_KEY
    has_key = bool(active_key and len(active_key) > 8)

    # Mask key for secure display
    masked_key = ""
    if has_key:
        masked_key = active_key[:4] + "..." + active_key[-4:] if len(active_key) >= 8 else "****"

    return jsonify({
        "success": True,
        "gemini_configured": has_key,
        "masked_key": masked_key,
        "model_name": Config.GEMINI_MODEL,
        "default_demo": Config.DEMO_MODE_DEFAULT
    })

@api_bp.route("/settings/api-key", methods=["POST"])
def update_api_key():
    """Updates runtime Gemini API key in session."""
    payload = request.get_json(silent=True) or {}
    new_key = payload.get("api_key", "").strip()

    if not new_key:
        session.pop("custom_gemini_api_key", None)
        return jsonify({"success": True, "message": "Custom API key cleared. Reverting to environment default."})

    # Test key with GeminiService
    test_svc = GeminiService(api_key=new_key, model_name=Config.GEMINI_MODEL)
    try:
        # Lightweight check
        client = test_svc.get_client()
        session["custom_gemini_api_key"] = new_key
        return jsonify({"success": True, "message": "Gemini API key validated and configured for current session."})
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to validate key: {str(e)}"}), 400

@api_bp.route("/export/<int:analysis_id>/<string:format_type>", methods=["GET"])
def export_report(analysis_id, format_type):
    """Exports structured analysis report as formatted Markdown or JSON."""
    record = db_session.query(Analysis).filter_by(id=analysis_id).first()
    if not record:
        return jsonify({"success": False, "error": "Analysis not found."}), 404

    data = record.to_full_dict()
    report = data.get("report", {})

    if format_type.lower() == "json":
        json_output = json.dumps(data, indent=2)
        return Response(
            json_output,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment;filename=resumeiq_report_{analysis_id}.json"}
        )
    elif format_type.lower() in ("md", "markdown"):
        # Format comprehensive markdown document
        md_lines = [
            f"# ResumeIQ Analysis Report — {record.candidate_name}",
            f"**Target Role:** {record.job_title} | **Company:** {record.company_name}",
            f"**Date:** {data['created_at']} | **Engine:** {record.model_used}",
            "",
            "## Scores & Indicators",
            f"- **Job Match Alignment:** {record.job_match_score}%" if record.job_match_score is not None else "- **Job Match:** Not evaluated (No JD provided)",
            f"- **ATS Readiness Score:** {record.ats_readiness_score}%",
            "",
            "## Executive Summary",
            record.summary,
            "",
            "## Key Strengths",
        ]
        for s in report.get("strengths", []):
            md_lines.append(f"- {s}")

        md_lines.extend(["", "## Areas for Improvement"])
        for w in report.get("weaknesses", []):
            md_lines.append(f"- {w}")

        if report.get("matched_skills"):
            md_lines.extend(["", "## Matched Technical Skills"])
            for m in report.get("matched_skills", []):
                md_lines.append(f"- **{m['skill']}** ({m.get('category', 'Technical')}) — Evidence: {m.get('evidence', 'Confirmed')}")

        if report.get("missing_skills"):
            md_lines.extend(["", "## Identified Skill Gaps (Missing Evidence)"])
            for m in report.get("missing_skills", []):
                md_lines.append(f"- **{m['skill']}** ({m.get('type', 'Required')}): {m.get('explanation', '')}")

        if report.get("bullet_improvements"):
            md_lines.extend(["", "## Improved Bullet Points (XYZ Formula)"])
            for b in report.get("bullet_improvements", []):
                md_lines.append(f"**Original:** {b.get('original')}")
                final_text = b.get('user_edited_text') or b.get('revised')
                md_lines.append(f"**Revised:** {final_text}")
                md_lines.append(f"*Note:* {b.get('what_changed', '')}\n")

        md_lines.extend([
            "",
            "---",
            "**Academic Notice:** This evaluation is generated by ResumeIQ for educational and diagnostic purposes. "
            "It does not guarantee interview shortlisting or hiring success."
        ])

        return Response(
            "\n".join(md_lines),
            mimetype="text/markdown",
            headers={"Content-Disposition": f"attachment;filename=resumeiq_report_{analysis_id}.md"}
        )
    else:
        return jsonify({"success": False, "error": "Supported export formats: 'json', 'markdown'"}), 400
