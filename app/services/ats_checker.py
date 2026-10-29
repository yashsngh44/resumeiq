import re
from typing import Dict, Any, List

class ATSChecker:
    """
    Deterministic, rule-based formatting and structure readiness evaluator.
    Evaluates key mechanical factors parsed by applicant tracking systems (ATS).
    Transparently discloses rules, score contributions, and actionable remediation steps.
    """

    ACTION_VERBS = {
        "built", "developed", "engineered", "designed", "implemented", "created",
        "optimized", "spearheaded", "orchestrated", "architected", "automated",
        "reduced", "increased", "boosted", "deployed", "scaled", "led", "managed",
        "analyzed", "collaborated", "delivered", "integrated", "streamlined", "resolved"
    }

    METRIC_PATTERNS = [
        re.compile(r'\b\d+%\b'),                      # e.g., 25%
        re.compile(r'[\$€£₹]\s*\d+(?:[.,]\d+)?\s*[kmbKMB]?'), # e.g., $50k
        re.compile(r'\b\d+(?:[.,]\d+)?\s*(?:x|times)\b', re.IGNORECASE), # e.g., 3x, 2 times
        re.compile(r'\b(?:reduced|increased|improved|saved)\s+by\s+\d+', re.IGNORECASE),
        re.compile(r'\b\d{2,}\+?\s*(?:users|clients|customers|requests|queries|downloads|students)\b', re.IGNORECASE)
    ]

    @classmethod
    def evaluate(cls, parsed_doc: Dict[str, Any], job_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Runs full deterministic ATS evaluation suite.
        Returns a transparent scorecard, total score (0-100), and breakdown.
        """
        checks: List[Dict[str, Any]] = []
        earned_points = 0.0
        total_possible = 100.0

        raw_text = parsed_doc.get("raw_text", "")
        contact = parsed_doc.get("contact_info", {})
        sections = parsed_doc.get("sections", {})
        word_count = parsed_doc.get("word_count", 0)
        page_count = parsed_doc.get("page_count", 1)
        bullet_points = parsed_doc.get("bullet_points", [])

        # ---------------------------------------------------------------------
        # 1. Contact Information Integrity (Total: 25 pts)
        # ---------------------------------------------------------------------
        # Email (10 pts)
        if contact.get("email"):
            earned_points += 10.0
            checks.append({
                "category": "Contact Information",
                "name": "Email Address",
                "status": "passed",
                "score": 10.0,
                "max_score": 10.0,
                "detail": f"Valid email detected: {contact['email']}",
                "recommendation": "Maintain clear email address at the top of your resume header."
            })
        else:
            checks.append({
                "category": "Contact Information",
                "name": "Email Address",
                "status": "failed",
                "score": 0.0,
                "max_score": 10.0,
                "detail": "No standard email address detected.",
                "recommendation": "Add a professional email address (e.g. name@domain.com) clearly in your header."
            })

        # Phone Number (10 pts)
        if contact.get("phone"):
            earned_points += 10.0
            checks.append({
                "category": "Contact Information",
                "name": "Phone Number",
                "status": "passed",
                "score": 10.0,
                "max_score": 10.0,
                "detail": f"Phone number detected: {contact['phone']}",
                "recommendation": "Ensure your phone number includes country/area code."
            })
        else:
            checks.append({
                "category": "Contact Information",
                "name": "Phone Number",
                "status": "warning",
                "score": 0.0,
                "max_score": 10.0,
                "detail": "No phone number pattern found.",
                "recommendation": "Include an active mobile number so recruiters can quickly schedule phone screens."
            })

        # Professional Links (5 pts)
        has_link = contact.get("has_linkedin") or contact.get("has_github")
        if has_link:
            earned_points += 5.0
            links = []
            if contact.get("linkedin"): links.append("LinkedIn")
            if contact.get("github"): links.append("GitHub")
            checks.append({
                "category": "Contact Information",
                "name": "Professional Profiles",
                "status": "passed",
                "score": 5.0,
                "max_score": 5.0,
                "detail": f"Profiles found: {', '.join(links)}",
                "recommendation": "Keep public profile links updated and hyperlinked."
            })
        else:
            checks.append({
                "category": "Contact Information",
                "name": "Professional Profiles",
                "status": "warning",
                "score": 2.0,
                "max_score": 5.0,
                earned_points: 2.0,
                "detail": "No LinkedIn or GitHub URL detected.",
                "recommendation": "Include a customized LinkedIn URL and relevant code repository or portfolio link."
            })
            earned_points += 2.0

        # ---------------------------------------------------------------------
        # 2. Section Organization & Standard Headings (Total: 30 pts)
        # ---------------------------------------------------------------------
        core_sections = [
            ("experience", "Work Experience", 10.0),
            ("education", "Education", 10.0),
            ("skills", "Skills Section", 10.0)
        ]

        for sec_key, sec_title, max_pts in core_sections:
            if sec_key in sections and len(sections[sec_key].strip()) > 20:
                earned_points += max_pts
                checks.append({
                    "category": "Section Structure",
                    "name": f"{sec_title} Section",
                    "status": "passed",
                    "score": max_pts,
                    "max_score": max_pts,
                    "detail": f"Standard '{sec_title}' heading detected with content.",
                    "recommendation": "Maintain standard section naming conventions for reliable parsing."
                })
            else:
                checks.append({
                    "category": "Section Structure",
                    "name": f"{sec_title} Section",
                    "status": "failed",
                    "score": 0.0,
                    "max_score": max_pts,
                    "detail": f"Standard '{sec_title}' heading not recognized or section is empty.",
                    "recommendation": f"Ensure you have a distinct section titled '{sec_title}'. Avoid creative headings like 'Where I have been' which confuse ATS parsers."
                })

        # ---------------------------------------------------------------------
        # 3. Document Length & Word Count (Total: 15 pts)
        # ---------------------------------------------------------------------
        # Standard 1-page to 2-page resume is ~350 - 1000 words
        if 350 <= word_count <= 1100:
            earned_points += 15.0
            checks.append({
                "category": "Content Volume",
                "name": "Word Count",
                "status": "passed",
                "score": 15.0,
                "max_score": 15.0,
                "detail": f"Healthy word count ({word_count} words, approx. {page_count} page(s)).",
                "recommendation": "Content volume is balanced for typical early-to-mid career roles."
            })
        elif word_count < 350:
            earned_pts = max(3.0, (word_count / 350.0) * 15.0)
            earned_points += earned_pts
            checks.append({
                "category": "Content Volume",
                "name": "Word Count",
                "status": "warning",
                "score": round(earned_pts, 1),
                "max_score": 15.0,
                "detail": f"Resume is brief ({word_count} words). May lack sufficient technical depth.",
                "recommendation": "Expand on your project details, technologies used, responsibilities, and quantified impacts."
            })
        else: # > 1100 words
            earned_pts = 10.0
            earned_points += earned_pts
            checks.append({
                "category": "Content Volume",
                "name": "Word Count",
                "status": "warning",
                "score": earned_pts,
                "max_score": 15.0,
                "detail": f"Resume is on the longer side ({word_count} words, approx {page_count} pages).",
                "recommendation": "For candidates under 5-8 years of experience, a concise 1-page resume (~450-700 words) is preferred by recruiters."
            })

        # ---------------------------------------------------------------------
        # 4. Action Verbs & Impact Metrics (Total: 15 pts)
        # ---------------------------------------------------------------------
        text_lower = raw_text.lower()
        verbs_found = [v for v in cls.ACTION_VERBS if re.search(r'\b' + v + r'\b', text_lower)]
        
        # Action verbs check (8 pts)
        if len(verbs_found) >= 5:
            earned_points += 8.0
            checks.append({
                "category": "Impact Language",
                "name": "Strong Action Verbs",
                "status": "passed",
                "score": 8.0,
                "max_score": 8.0,
                "detail": f"Found {len(verbs_found)} dynamic action verbs (e.g., {', '.join(verbs_found[:4])}).",
                "recommendation": "Continue starting each bullet point with a decisive past-tense action verb."
            })
        elif len(verbs_found) >= 2:
            earned_points += 4.0
            checks.append({
                "category": "Impact Language",
                "name": "Strong Action Verbs",
                "status": "warning",
                "score": 4.0,
                "max_score": 8.0,
                "detail": f"Only {len(verbs_found)} distinct action verbs found ({', '.join(verbs_found)}).",
                "recommendation": "Replace passive verbs ('responsible for', 'worked on') with active engineering verbs ('engineered', 'deployed', 'spearheaded')."
            })
        else:
            checks.append({
                "category": "Impact Language",
                "name": "Strong Action Verbs",
                "status": "failed",
                "score": 0.0,
                "max_score": 8.0,
                "detail": "Minimal action verbs detected. Text may read like a passive job description.",
                "recommendation": "Rewrite bullet points using the formula: Action Verb + Task + Quantifiable Result."
            })

        # Quantifiable metrics check (7 pts)
        metric_hits = 0
        for pattern in cls.METRIC_PATTERNS:
            metric_hits += len(pattern.findall(raw_text))

        if metric_hits >= 3:
            earned_points += 7.0
            checks.append({
                "category": "Impact Language",
                "name": "Quantifiable Metrics",
                "status": "passed",
                "score": 7.0,
                "max_score": 7.0,
                "detail": f"Detected {metric_hits} quantitative indicators (percentages, numbers, scale).",
                "recommendation": "Great job grounding achievements with numerical evidence."
            })
        elif metric_hits >= 1:
            earned_points += 3.5
            checks.append({
                "category": "Impact Language",
                "name": "Quantifiable Metrics",
                "status": "warning",
                "score": 3.5,
                "max_score": 7.0,
                "detail": f"Only {metric_hits} quantitative indicator detected.",
                "recommendation": "Add specific numbers: team size, database volume, latency improvements, user adoption, or test coverage."
            })
        else:
            checks.append({
                "category": "Impact Language",
                "name": "Quantifiable Metrics",
                "status": "failed",
                "score": 0.0,
                "max_score": 7.0,
                "detail": "No clear quantitative metrics (%, $, counts, scale) identified.",
                "recommendation": "Recruiters favor quantifiable achievements. Add real metrics wherever possible (e.g. 'reduced latency by 35%')."
            })

        # ---------------------------------------------------------------------
        # 5. Text Extraction & Formatting Cleanliness (Total: 15 pts)
        # ---------------------------------------------------------------------
        # Check non-ascii corruption ratio (often indicates weird PDF font encodings or glyph issues)
        non_ascii = len(re.findall(r'[^\x00-\x7F]', raw_text))
        total_chars = max(1, len(raw_text))
        non_ascii_ratio = non_ascii / total_chars

        if non_ascii_ratio < 0.05:
            earned_points += 15.0
            checks.append({
                "category": "Parser Health",
                "name": "Text Extraction Cleanliness",
                "status": "passed",
                "score": 15.0,
                "max_score": 15.0,
                "detail": f"Clean UTF-8 text extraction (character anomaly ratio {non_ascii_ratio*100:.1f}%).",
                "recommendation": "Text encoding is clean and readable by automated parsing engines."
            })
        else:
            earned_points += 7.0
            checks.append({
                "category": "Parser Health",
                "name": "Text Extraction Cleanliness",
                "status": "warning",
                "score": 7.0,
                "max_score": 15.0,
                "detail": f"High character anomaly ratio ({non_ascii_ratio*100:.1f}% non-standard symbols or complex ligatures).",
                "recommendation": "Avoid decorative icons, unusual symbol bullet points, or complex multi-column text tables that disrupt standard PDF parsers."
            })

        # Final Score Normalization
        final_score = min(100.0, max(0.0, round(earned_points, 1)))

        # Qualitative Grade
        if final_score >= 85:
            grade = "Excellent"
            summary = "Your resume exhibits solid ATS compatibility, clear sectioning, and readable contact metadata."
        elif final_score >= 70:
            grade = "Good"
            summary = "Good baseline formatting, with minor opportunities to strengthen section headers, action verbs, or metrics."
        elif final_score >= 50:
            grade = "Needs Improvement"
            summary = "Key structural elements or contact items are missing or difficult for parsers to identify."
        else:
            grade = "Critical Attention"
            summary = "Significant formatting or structural issues detected that may cause standard applicant tracking systems to reject or misread the file."

        return {
            "score": final_score,
            "grade": grade,
            "summary": summary,
            "checks": checks,
            "passed_count": sum(1 for c in checks if c["status"] == "passed"),
            "warning_count": sum(1 for c in checks if c["status"] == "warning"),
            "failed_count": sum(1 for c in checks if c["status"] == "failed"),
            "is_deterministic": True,
            "disclaimer": (
                "Notice: This score is a deterministic, rule-based audit of document parsing readability, "
                "section organization, and contact presence. It is NOT an official ATS proprietary algorithm score "
                "and does not guarantee interview shortlisting."
            )
        }
