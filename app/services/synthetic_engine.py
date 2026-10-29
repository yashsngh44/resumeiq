from typing import Dict, Any, List
from .ats_checker import ATSChecker
from .job_matcher import JobMatcher
from .roadmap_generator import RoadmapGenerator
from .bullet_lab import BulletLab

class SyntheticEngine:
    """
    Local Heuristic Analysis Engine for Academic Demonstration Mode.
    Provides rigorous, evidence-grounded resume analysis without requiring external API calls.
    Every output is computed from actual document text and clearly tagged as Demo/Heuristic.
    """

    @classmethod
    def analyze(
        cls,
        parsed_doc: Dict[str, Any],
        job_description: str = "",
        job_title: str = "",
        company_name: str = ""
    ) -> Dict[str, Any]:
        """
        Executes a complete, evidence-based local analysis pipeline.
        Combines ATS rules, skill taxonomy matching, roadmap generation, and bullet rewrites.
        """
        raw_text = parsed_doc.get("raw_text", "")
        contact = parsed_doc.get("contact_info", {})
        sections = parsed_doc.get("sections", {})
        bullet_points = parsed_doc.get("bullet_points", [])
        has_jd = bool(job_description and job_description.strip())

        # 1. Deterministic ATS evaluation
        ats_result = ATSChecker.evaluate(parsed_doc)

        # 2. Skill Matching & Gap Engine (if JD provided)
        if has_jd:
            match_result = JobMatcher.match(raw_text, job_description, ats_result["score"])
            job_match_score = match_result["job_match_score"]
            matched_skills = match_result["matched_skills"]
            partial_skills = match_result["partial_skills"]
            missing_skills = match_result["missing_skills"]
            scoring_breakdown = match_result["scoring_breakdown"]
            target_skills = [s["skill"] for s in matched_skills + missing_skills]
        else:
            job_match_score = None
            matched_skills = []
            partial_skills = []
            missing_skills = []
            scoring_breakdown = None
            target_skills = []

        # 3. Personalized Career Roadmap
        if has_jd:
            roadmap = RoadmapGenerator.generate(missing_skills, partial_skills, job_title or "Target Role")
        else:
            # General skill enhancement roadmap based on sections
            roadmap = []

        # 4. Resume Improvement Lab Suggestions
        bullet_rewrites = BulletLab.batch_generate(bullet_points, target_skills, max_suggestions=6)

        # 5. Extract Qualitative Strengths & Growth Areas grounded in actual text
        strengths = cls._synthesize_strengths(parsed_doc, ats_result, matched_skills)
        weaknesses = cls._synthesize_weaknesses(parsed_doc, ats_result, missing_skills, has_jd)
        recommendations = cls._synthesize_recommendations(ats_result, missing_skills, bullet_rewrites, has_jd)

        # 6. Overall Summary
        candidate_name = parsed_doc.get("candidate_name", "Candidate")
        if has_jd:
            summary = (
                f"Resume for {candidate_name} analyzed against target role '{job_title or 'Specified Position'}'. "
                f"Candidate matches {len(matched_skills)} key technical competencies with {len(partial_skills)} transferable skill bridges, "
                f"and {len(missing_skills)} unverified requirements. ATS structural readiness is rated at {ats_result['score']}%. "
                f"Overall job alignment index is computed at {job_match_score}%."
            )
        else:
            summary = (
                f"General structural and content audit completed for {candidate_name}. "
                f"Resume contains {parsed_doc.get('word_count', 0)} words across {len(sections)} distinct sections with "
                f"{ats_result['score']}% ATS structural formatting readiness. Provide a target job description to unlock role-specific skill gap analysis."
            )

        return {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "company_name": company_name,
            "has_job_description": has_jd,
            "job_match_score": job_match_score,
            "ats_readiness_score": ats_result["score"],
            "ats_details": ats_result,
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "matched_skills": matched_skills,
            "partial_skills": partial_skills,
            "missing_skills": missing_skills,
            "scoring_breakdown": scoring_breakdown,
            "roadmap": roadmap,
            "bullet_improvements": bullet_rewrites,
            "is_demo_mode": True,
            "model_used": "Academic Heuristic Engine (Offline Heuristic Mode)",
            "limitations": [
                "Evaluation produced by deterministic local parsing rules and curated keyword heuristics.",
                "Semantic reasoning is limited to the predefined taxonomy of software engineering and cloud technologies.",
                "To enable dynamic LLM deep reasoning and conversational feedback, configure a valid GEMINI_API_KEY in Settings."
            ]
        }

    @classmethod
    def _synthesize_strengths(cls, parsed_doc: Dict[str, Any], ats: Dict[str, Any], matched: List[Dict[str, Any]]) -> List[str]:
        strengths = []
        if ats["score"] >= 75:
            strengths.append(f"Strong overall ATS formatting score ({ats['score']}%) with compliant section headers and standard layout.")
        if parsed_doc.get("contact_info", {}).get("email") and parsed_doc.get("contact_info", {}).get("phone"):
            strengths.append("Complete, easily parseable contact details (verified email and phone).")
        if matched:
            top_skills = [m["skill"] for m in matched[:4]]
            strengths.append(f"Verified alignment on critical technical competencies: {', '.join(top_skills)}.")
        if parsed_doc.get("bullet_points") and len(parsed_doc.get("bullet_points")) >= 5:
            strengths.append(f"Rich descriptive project and experience history ({len(parsed_doc['bullet_points'])} distinct bullet points).")
        if not strengths:
            strengths.append("Foundational resume structure present with readable text extraction.")
        return strengths

    @classmethod
    def _synthesize_weaknesses(cls, parsed_doc: Dict[str, Any], ats: Dict[str, Any], missing: List[Dict[str, Any]], has_jd: bool) -> List[str]:
        weaknesses = []
        for check in ats.get("checks", []):
            if check["status"] == "failed":
                weaknesses.append(f"{check['category']}: {check['detail']}")
        
        if has_jd and missing:
            top_missing = [m["skill"] for m in missing[:3]]
            weaknesses.append(f"Target role requirements with unverified evidence in resume: {', '.join(top_missing)}.")
        
        if parsed_doc.get("word_count", 0) < 300:
            weaknesses.append("Resume length is shorter than recommended (less than 300 words), lacking technical depth.")
        elif parsed_doc.get("word_count", 0) > 1200:
            weaknesses.append("Content exceeds 1,200 words; consider tightening focus for a concise 1-page impact format.")

        if not weaknesses:
            weaknesses.append("No critical structural weaknesses found; focus on quantifying bullet points with metrics.")
        return weaknesses

    @classmethod
    def _synthesize_recommendations(cls, ats: Dict[str, Any], missing: List[Dict[str, Any]], bullets: List[Dict[str, Any]], has_jd: bool) -> List[str]:
        recs = []
        if has_jd and missing:
            recs.append(f"Review the {len(missing)} identified skill gaps in the Career Roadmap. If you have experience with these tools, explicitly add them to your skills and project bullets.")
        
        needs_metrics = sum(1 for b in bullets if b.get("needs_user_metric"))
        if needs_metrics > 0:
            recs.append(f"Quantify {needs_metrics} bullet points in the Resume Improvement Lab with real business/performance metrics (e.g., latency, users, scale).")

        for check in ats.get("checks", []):
            if check["status"] in ("failed", "warning") and check.get("recommendation"):
                recs.append(check["recommendation"])

        return recs[:5]
