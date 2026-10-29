import re
from typing import Dict, Any, List, Set, Tuple

class JobMatcher:
    """
    Analyzes resume text against a target job description.
    Extracts required and preferred skills, matches them with semantic equivalence,
    identifies skill gaps with grounded evidence quotes, and calculates a transparent score.
    """

    # Comprehensive skill dictionary organized by domain
    SKILL_TAXONOMY: Dict[str, Dict[str, Any]] = {
        # Programming Languages
        "python": {"canonical": "Python", "category": "Languages", "synonyms": ["python3", "python 3", "py"]},
        "javascript": {"canonical": "JavaScript", "category": "Languages", "synonyms": ["js", "ecmascript", "es6"]},
        "typescript": {"canonical": "TypeScript", "category": "Languages", "synonyms": ["ts"]},
        "java": {"canonical": "Java", "category": "Languages", "synonyms": ["core java", "j2ee", "jdk"]},
        "c++": {"canonical": "C++", "category": "Languages", "synonyms": ["cpp", "c plus plus"]},
        "c#": {"canonical": "C#", "category": "Languages", "synonyms": ["csharp", "c sharp", ".net c#"]},
        "golang": {"canonical": "Go", "category": "Languages", "synonyms": ["go", "golang"]},
        "rust": {"canonical": "Rust", "category": "Languages", "synonyms": ["rustlang"]},
        "ruby": {"canonical": "Ruby", "category": "Languages", "synonyms": ["ruby on rails", "rails"]},
        "php": {"canonical": "PHP", "category": "Languages", "synonyms": ["modern php"]},
        "sql": {"canonical": "SQL", "category": "Languages", "synonyms": ["structured query language", "tsql", "plsql"]},
        "html": {"canonical": "HTML5", "category": "Languages", "synonyms": ["html", "html5"]},
        "css": {"canonical": "CSS3", "category": "Languages", "synonyms": ["css", "css3", "sass", "scss"]},
        "bash": {"canonical": "Bash / Shell", "category": "Languages", "synonyms": ["shell script", "bash scripting", "powershell", "zsh"]},

        # Frameworks & Libraries
        "react": {"canonical": "React", "category": "Frameworks", "synonyms": ["reactjs", "react.js", "react native"]},
        "vue": {"canonical": "Vue.js", "category": "Frameworks", "synonyms": ["vue", "vuejs", "vue3"]},
        "angular": {"canonical": "Angular", "category": "Frameworks", "synonyms": ["angularjs", "angular 2+"]},
        "nextjs": {"canonical": "Next.js", "category": "Frameworks", "synonyms": ["next.js", "next js"]},
        "nodejs": {"canonical": "Node.js", "category": "Frameworks", "synonyms": ["node", "node.js", "expressjs", "express.js", "express"]},
        "django": {"canonical": "Django", "category": "Frameworks", "synonyms": ["django rest framework", "drf"]},
        "flask": {"canonical": "Flask", "category": "Frameworks", "synonyms": ["flask microframework"]},
        "fastapi": {"canonical": "FastAPI", "category": "Frameworks", "synonyms": ["fast api"]},
        "spring": {"canonical": "Spring Boot", "category": "Frameworks", "synonyms": ["spring boot", "spring framework", "spring"]},
        "pytorch": {"canonical": "PyTorch", "category": "AI/Data", "synonyms": ["torch"]},
        "tensorflow": {"canonical": "TensorFlow", "category": "AI/Data", "synonyms": ["tf", "keras"]},
        "pandas": {"canonical": "Pandas", "category": "AI/Data", "synonyms": ["pandas library"]},
        "numpy": {"canonical": "NumPy", "category": "AI/Data", "synonyms": ["numpy library"]},
        "scikit-learn": {"canonical": "Scikit-Learn", "category": "AI/Data", "synonyms": ["sklearn", "scikit learn"]},

        # Cloud & Infrastructure
        "aws": {"canonical": "AWS", "category": "Cloud & DevOps", "synonyms": ["amazon web services", "ec2", "s3", "lambda"]},
        "azure": {"canonical": "Azure", "category": "Cloud & DevOps", "synonyms": ["microsoft azure", "azure cloud"]},
        "gcp": {"canonical": "Google Cloud (GCP)", "category": "Cloud & DevOps", "synonyms": ["google cloud platform", "google cloud"]},
        "docker": {"canonical": "Docker", "category": "Cloud & DevOps", "synonyms": ["containerization", "containers", "dockerfile"]},
        "kubernetes": {"canonical": "Kubernetes", "category": "Cloud & DevOps", "synonyms": ["k8s", "helm"]},
        "cicd": {"canonical": "CI/CD", "category": "Cloud & DevOps", "synonyms": ["continuous integration", "continuous deployment", "github actions", "gitlab ci", "jenkins"]},
        "git": {"canonical": "Git", "category": "Cloud & DevOps", "synonyms": ["github", "gitlab", "version control"]},
        "linux": {"canonical": "Linux", "category": "Cloud & DevOps", "synonyms": ["unix", "ubuntu", "debian", "centos", "redhat"]},
        "terraform": {"canonical": "Terraform", "category": "Cloud & DevOps", "synonyms": ["iac", "infrastructure as code"]},

        # Databases
        "postgresql": {"canonical": "PostgreSQL", "category": "Databases", "synonyms": ["postgres", "psql"]},
        "mysql": {"canonical": "MySQL", "category": "Databases", "synonyms": ["mariadb"]},
        "mongodb": {"canonical": "MongoDB", "category": "Databases", "synonyms": ["mongo", "nosql"]},
        "redis": {"canonical": "Redis", "category": "Databases", "synonyms": ["redis cache"]},
        "sqlite": {"canonical": "SQLite", "category": "Databases", "synonyms": ["sqlite3"]},
        "dynamodb": {"canonical": "DynamoDB", "category": "Databases", "synonyms": ["amazon dynamodb"]},

        # Architecture & Methods
        "rest": {"canonical": "RESTful APIs", "category": "Architecture", "synonyms": ["rest api", "rest", "restful", "web apis"]},
        "graphql": {"canonical": "GraphQL", "category": "Architecture", "synonyms": ["graph ql", "apollo"]},
        "microservices": {"canonical": "Microservices", "category": "Architecture", "synonyms": ["microservice architecture", "distributed systems"]},
        "testing": {"canonical": "Unit & Integration Testing", "category": "Architecture", "synonyms": ["unit test", "tdd", "pytest", "jest", "mocking", "test automation"]},
        "agile": {"canonical": "Agile / Scrum", "category": "Methodology", "synonyms": ["scrum", "kanban", "sprints"]},
        "system-design": {"canonical": "System Design", "category": "Architecture", "synonyms": ["software architecture", "scalability", "high availability"]}
    }

    # Skill Family Relationships for Partial Matching
    SKILL_FAMILIES = {
        "backend_frameworks": {"django", "flask", "fastapi", "spring", "nodejs", "ruby"},
        "frontend_frameworks": {"react", "vue", "angular", "nextjs"},
        "cloud_providers": {"aws", "azure", "gcp"},
        "sql_databases": {"postgresql", "mysql", "sqlite"},
        "nosql_databases": {"mongodb", "redis", "dynamodb"},
        "ml_frameworks": {"pytorch", "tensorflow", "scikit-learn"}
    }

    @classmethod
    def match(
        cls,
        resume_text: str,
        job_description: str,
        ats_score: float = 80.0
    ) -> Dict[str, Any]:
        """
        Analyzes the resume against the target job description.
        Computes transparent job match indicator and identifies categorized gaps.
        """
        jd_lower = job_description.lower()
        resume_lower = resume_text.lower()
        resume_sentences = cls._split_into_sentences(resume_text)

        # 1. Extract requirements from Job Description
        required_keys, preferred_keys = cls._extract_jd_skills(jd_lower)

        # Fallback if JD is brief or unstructured
        if not required_keys and not preferred_keys:
            all_found = cls._find_any_taxonomy_skills(jd_lower)
            # Default split: first 60% required, 40% preferred
            skill_list = list(all_found)
            split_idx = max(1, int(len(skill_list) * 0.6))
            required_keys = set(skill_list[:split_idx])
            preferred_keys = set(skill_list[split_idx:])

        # 2. Match each requirement against the resume
        matched_skills: List[Dict[str, Any]] = []
        partial_skills: List[Dict[str, Any]] = []
        missing_skills: List[Dict[str, Any]] = []

        all_target_keys = [(k, True) for k in required_keys] + [(k, False) for k in preferred_keys]

        for skill_key, is_required in all_target_keys:
            skill_info = cls.SKILL_TAXONOMY.get(skill_key, {
                "canonical": skill_key.capitalize(),
                "category": "Technical",
                "synonyms": []
            })
            canonical_name = skill_info["canonical"]
            category = skill_info["category"]
            req_type = "Required" if is_required else "Preferred"

            # Check direct or synonym match
            match_found, evidence_quote = cls._check_skill_presence(skill_key, skill_info, resume_lower, resume_sentences)

            if match_found:
                matched_skills.append({
                    "skill": canonical_name,
                    "category": category,
                    "type": req_type,
                    "status": "matched",
                    "confidence": "High",
                    "evidence": evidence_quote or "Direct mention confirmed in resume text.",
                    "explanation": f"Candidate directly demonstrates {canonical_name} in their resume content."
                })
            else:
                # Check for partial / family match (e.g., knows Flask, role asks for Django)
                partial_match, family_skill = cls._check_partial_family(skill_key, resume_lower)
                if partial_match:
                    partial_skills.append({
                        "skill": canonical_name,
                        "category": category,
                        "type": req_type,
                        "status": "partial",
                        "confidence": "Moderate",
                        "related_skill_found": family_skill,
                        "evidence": f"Found related capability: {family_skill}",
                        "explanation": (
                            f"While '{canonical_name}' is not explicitly listed, candidate demonstrates strong "
                            f"competency in related technology '{family_skill}'. Knowledge is transferrable."
                        )
                    })
                else:
                    missing_skills.append({
                        "skill": canonical_name,
                        "category": category,
                        "type": req_type,
                        "status": "missing",
                        "confidence": "N/A (Missing Evidence)",
                        "evidence": None,
                        "explanation": (
                            f"No explicit mention or evidence of '{canonical_name}' was found in the resume. "
                            "Notice: This represents unverified written evidence, not a verified absence of candidate capability."
                        )
                    })

        # 3. Transparent Scoring Calculation
        # Counts
        total_req = len(required_keys)
        total_pref = len(preferred_keys)

        matched_req = sum(1 for s in matched_skills if s["type"] == "Required")
        partial_req = sum(1 for s in partial_skills if s["type"] == "Required")

        matched_pref = sum(1 for s in matched_skills if s["type"] == "Preferred")
        partial_pref = sum(1 for s in partial_skills if s["type"] == "Preferred")

        # Score calculations (Full match = 1.0, Partial = 0.5)
        req_score = 100.0 if total_req == 0 else min(100.0, ((matched_req * 1.0 + partial_req * 0.5) / total_req) * 100.0)
        pref_score = 100.0 if total_pref == 0 else min(100.0, ((matched_pref * 1.0 + partial_pref * 0.5) / total_pref) * 100.0)

        # Experience Alignment Heuristic (15% weight)
        exp_score = cls._evaluate_experience_alignment(resume_text, job_description)

        # ATS Readiness input (10% weight)
        ats_contrib = min(100.0, max(0.0, ats_score))

        # Overall Weighted Score Formula:
        # Score = 0.50 * ReqScore + 0.25 * PrefScore + 0.15 * ExpScore + 0.10 * ATSScore
        weighted_score = (0.50 * req_score) + (0.25 * pref_score) + (0.15 * exp_score) + (0.10 * ats_contrib)
        final_score = round(min(100.0, max(0.0, weighted_score)), 1)

        # Qualitative Match Tier
        if final_score >= 80:
            match_tier = "Strong Alignment"
            badge_color = "success"
        elif final_score >= 60:
            match_tier = "Moderate Alignment"
            badge_color = "warning"
        elif final_score >= 40:
            match_tier = "Developing Alignment"
            badge_color = "secondary"
        else:
            match_tier = "Low Alignment / Significant Gaps"
            badge_color = "danger"

        return {
            "job_match_score": final_score,
            "match_tier": match_tier,
            "badge_color": badge_color,
            "scoring_breakdown": {
                "formula": "Score = (0.50 * RequiredSkills) + (0.25 * PreferredSkills) + (0.15 * ExperienceAlignment) + (0.10 * ATSReadiness)",
                "weights": {
                    "required_skills": "50%",
                    "preferred_skills": "25%",
                    "experience_alignment": "15%",
                    "ats_formatting": "10%"
                },
                "sub_scores": {
                    "required_skills_score": round(req_score, 1),
                    "preferred_skills_score": round(pref_score, 1),
                    "experience_alignment_score": round(exp_score, 1),
                    "ats_formatting_score": round(ats_contrib, 1)
                },
                "details": {
                    "total_required": total_req,
                    "matched_required": matched_req,
                    "partial_required": partial_req,
                    "total_preferred": total_pref,
                    "matched_preferred": matched_pref,
                    "partial_preferred": partial_pref
                }
            },
            "matched_skills": matched_skills,
            "partial_skills": partial_skills,
            "missing_skills": missing_skills,
            "disclaimer": (
                "Academic Transparency Disclaimer: This job-match indicator is a deterministic heuristic "
                "measuring keyword alignment, recognized skill families, and document readability against "
                "the provided text. It is NOT an official commercial ATS algorithm score and does not guarantee "
                "interview selection or hiring success."
            )
        }

    @classmethod
    def _extract_jd_skills(cls, jd_lower: str) -> Tuple[Set[str], Set[str]]:
        """Splits job description into required and preferred sections and extracts skills."""
        required_keys: Set[str] = set()
        preferred_keys: Set[str] = set()

        # Split JD by sections if headers exist
        req_pattern = re.compile(r'(?:requirements|must have|minimum qualifications|qualifications|required skills|what you will need|what you need)[:\n]', re.IGNORECASE)
        pref_pattern = re.compile(r'(?:nice to have|preferred|bonus|desirable|plus|preferred qualifications)[:\n]', re.IGNORECASE)

        req_matches = list(req_pattern.finditer(jd_lower))
        pref_matches = list(pref_pattern.finditer(jd_lower))

        if req_matches or pref_matches:
            # If explicit headings found, parse by chunks
            all_spans = []
            for m in req_matches:
                all_spans.append((m.start(), "req"))
            for m in pref_matches:
                all_spans.append((m.start(), "pref"))
            all_spans.sort(key=lambda x: x[0])

            for i, (start_idx, s_type) in enumerate(all_spans):
                end_idx = all_spans[i+1][0] if i+1 < len(all_spans) else len(jd_lower)
                chunk = jd_lower[start_idx:end_idx]
                skills_in_chunk = cls._find_any_taxonomy_skills(chunk)
                if s_type == "req":
                    required_keys.update(skills_in_chunk)
                else:
                    preferred_keys.update(skills_in_chunk)
        else:
            # Default fallback: scan entire JD
            all_found = cls._find_any_taxonomy_skills(jd_lower)
            required_keys = all_found

        return required_keys, preferred_keys

    @classmethod
    def _find_any_taxonomy_skills(cls, text: str) -> Set[str]:
        """Finds any skill keys from the taxonomy present in the given text."""
        found = set()
        for key, info in cls.SKILL_TAXONOMY.items():
            # Check key
            if re.search(r'\b' + re.escape(key) + r'\b', text):
                found.add(key)
                continue
            # Check synonyms
            for syn in info.get("synonyms", []):
                if re.search(r'\b' + re.escape(syn) + r'\b', text):
                    found.add(key)
                    break
        return found

    @classmethod
    def _check_skill_presence(
        cls,
        skill_key: str,
        skill_info: Dict[str, Any],
        resume_lower: str,
        resume_sentences: List[str]
    ) -> Tuple[bool, str]:
        """Checks if a skill or any of its synonyms is found in the resume, returning a quote."""
        candidates = [skill_key] + skill_info.get("synonyms", [])
        for cand in candidates:
            pattern = re.compile(r'\b' + re.escape(cand) + r'\b')
            if pattern.search(resume_lower):
                # Find matching original sentence
                for sentence in resume_sentences:
                    if pattern.search(sentence.lower()):
                        clean_sentence = sentence.strip()
                        if len(clean_sentence) > 160:
                            clean_sentence = clean_sentence[:157] + "..."
                        return True, f'"{clean_sentence}"'
                return True, f'Mentioned as "{cand.title()}" in resume.'
        return False, ""

    @classmethod
    def _check_partial_family(cls, skill_key: str, resume_lower: str) -> Tuple[bool, str]:
        """Checks if candidate has a related skill in the same conceptual family."""
        for family_name, members in cls.SKILL_FAMILIES.items():
            if skill_key in members:
                for other_member in members:
                    if other_member != skill_key:
                        other_info = cls.SKILL_TAXONOMY.get(other_member, {})
                        candidates = [other_member] + other_info.get("synonyms", [])
                        for cand in candidates:
                            if re.search(r'\b' + re.escape(cand) + r'\b', resume_lower):
                                return True, other_info.get("canonical", other_member.title())
        return False, ""

    @classmethod
    def _evaluate_experience_alignment(cls, resume_text: str, jd_text: str) -> float:
        """Heuristic evaluation of years/seniority level between resume and JD."""
        # Find years of experience mentioned in JD
        jd_years_match = re.search(r'(\d+)\+?\s*(?:-\s*\d+)?\s*years?(?:\s+of)?\s+experience', jd_text, re.IGNORECASE)
        required_years = int(jd_years_match.group(1)) if jd_years_match else 1

        # Check resume for years patterns
        resume_years_matches = re.findall(r'(\d+)\+?\s*years?(?:\s+of)?\s+experience', resume_text, re.IGNORECASE)
        resume_years = max([int(y) for y in resume_years_matches], default=0)

        # Count graduation or work timeline hints
        year_mentions = re.findall(r'\b(201\d|202\d)\b', resume_text)
        if len(year_mentions) >= 2:
            years = [int(y) for y in year_mentions]
            timeline_span = max(years) - min(years)
            resume_years = max(resume_years, min(timeline_span, 10))

        if required_years <= 1:
            return 95.0
        elif resume_years >= required_years:
            return 100.0
        elif resume_years > 0:
            return max(50.0, round((resume_years / required_years) * 90.0, 1))
        else:
            # Baseline entry level
            return 70.0

    @classmethod
    def _split_into_sentences(cls, text: str) -> List[str]:
        """Splits document text into readable sentences/clauses for evidence extraction."""
        # Split on newlines, bullets, or punctuation
        raw_parts = re.split(r'[\n\r•\-\*]|\.(?=\s+[A-Z])', text)
        sentences = []
        for part in raw_parts:
            s = part.strip()
            if len(s) > 15:
                sentences.append(s)
        return sentences
