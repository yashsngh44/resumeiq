import re
from typing import Dict, Any, List

class BulletLab:
    """
    Analyzes resume bullet points and generates evidence-grounded rewrites
    following the XYZ formula (Accomplished [X] as measured by [Y], by doing [Z]).
    Crucially: NEVER fabricates metrics or achievements. Instead, provides structured
    prompts asking the user for their verified factual figures.
    """

    PASSIVE_STARTERS = [
        (re.compile(r'^(?:responsible for|was responsible for)\s+', re.IGNORECASE), "Managed and executed"),
        (re.compile(r'^(?:worked on|worked with)\s+', re.IGNORECASE), "Developed and implemented"),
        (re.compile(r'^(?:helped with|helped to|assisted in|assisted with)\s+', re.IGNORECASE), "Collaborated to deliver"),
        (re.compile(r'^(?:tasked with|assigned to)\s+', re.IGNORECASE), "Spearheaded"),
        (re.compile(r'^(?:involved in)\s+', re.IGNORECASE), "Contributed to engineering"),
        (re.compile(r'^(?:duties included)\s+', re.IGNORECASE), "Delivered"),
    ]

    METRIC_REGEX = re.compile(r'(\b\d+%(?!\w)|[\$€£₹]\s*\d+|\b\d+\s*(?:k|m|million|users|clients|requests|queries|x|times)\b)', re.IGNORECASE)

    @classmethod
    def analyze_and_improve(
        cls,
        bullet_text: str,
        target_skills: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes a single resume bullet point and generates an honest,
        high-impact revision without inventing facts.
        """
        clean_bullet = bullet_text.strip()
        words = clean_bullet.split()
        
        # 1. Check for passive starters
        weak_starter_matched = None
        replacement_verb = "Engineered"
        revised_text = clean_bullet

        for pattern, strong_verb in cls.PASSIVE_STARTERS:
            if pattern.search(clean_bullet):
                weak_starter_matched = pattern.pattern
                replacement_verb = strong_verb
                revised_text = pattern.sub(strong_verb + " ", clean_bullet)
                break

        # If it starts with a lowercase word or plain noun, capitalize and lead with action
        if not weak_starter_matched and words:
            first_word = words[0].lower()
            if first_word.endswith("ing"):
                # e.g., "Building a web app" -> "Built a web app"
                past_tense_map = {
                    "building": "Built", "creating": "Created", "developing": "Developed",
                    "designing": "Designed", "writing": "Authored", "implementing": "Implemented",
                    "managing": "Managed", "maintaining": "Maintained", "testing": "Tested"
                }
                new_first = past_tense_map.get(first_word, first_word.capitalize())
                revised_text = new_first + " " + " ".join(words[1:])
                weak_starter_matched = f"Gerund '{first_word}'"

        # 2. Check for metric presence
        has_metric = bool(cls.METRIC_REGEX.search(clean_bullet))
        
        # 3. Connect to target requirement
        relevant_tech = "target core competencies"
        if target_skills:
            for s in target_skills:
                if s.lower() in clean_bullet.lower():
                    relevant_tech = s
                    break
            if relevant_tech == "target core competencies" and target_skills:
                relevant_tech = target_skills[0]

        # 4. Craft revised bullet and explanation
        changes = []
        user_prompt = None

        if weak_starter_matched:
            changes.append(f"Replaced passive phrasing with strong action verb '{replacement_verb}'")
        else:
            changes.append("Preserved active engineering verbs while tightening clarity")

        if not has_metric:
            changes.append("Added a quantifiable outcome placeholder using Google's XYZ formula")
            revised_text += f" [Add your real metric: e.g., improving response time by X% or serving N users]"
            user_prompt = "What was the measurable result of this work? (e.g., latency reduction, test coverage %, user count, or hours saved)"
        else:
            changes.append("Preserved existing quantifiable metric provided in resume")

        # Weakness diagnosis
        if weak_starter_matched and not has_metric:
            weakness = "Starts with passive wording and lacks quantifiable outcome or metrics."
        elif weak_starter_matched:
            weakness = "Uses passive job-duty language instead of decisive action-oriented verbs."
        elif not has_metric:
            weakness = "Explains the activity well but lacks a concrete measurable result (scale, speed, or impact)."
        else:
            weakness = "Minor formatting and flow refinement to highlight technical ownership."

        return {
            "original": clean_bullet,
            "revised": revised_text,
            "weakness_identified": weakness,
            "what_changed": "; ".join(changes) + ".",
            "job_requirement_supported": relevant_tech,
            "needs_user_metric": not has_metric,
            "user_metric_prompt": user_prompt,
            "status": "pending",
            "user_edited_text": revised_text
        }

    @classmethod
    def batch_generate(
        cls,
        bullet_points: List[Dict[str, Any]],
        target_skills: List[str] = None,
        max_suggestions: int = 5
    ) -> List[Dict[str, Any]]:
        """Selects the most impactful bullet points to rewrite."""
        results = []
        # Filter for candidates that need improvement (passive or lacking metrics)
        candidates = bullet_points[:12]  # Scan first 12
        
        for bp in candidates:
            text = bp.get("text", "") if isinstance(bp, dict) else str(bp)
            if len(text.split()) < 5:
                continue
            
            improvement = cls.analyze_and_improve(text, target_skills)
            # Give higher priority to bullets that had weaknesses
            results.append({
                "id": bp.get("id", f"b_{len(results)+1}"),
                **improvement
            })

            if len(results) >= max_suggestions:
                break

        return results
