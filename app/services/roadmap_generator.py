from typing import Dict, Any, List

class RoadmapGenerator:
    """
    Transforms identified skill gaps into a structured, prioritized, actionable learning roadmap.
    Provides verified documentation links, beginner actions, practical projects, and realistic effort estimates.
    """

    # Knowledge base of verified, reputable official documentation and curated guides (NO 404s/hallucinations)
    CURATED_RESOURCES: Dict[str, Dict[str, Any]] = {
        "Docker": {
            "why_it_matters": "Modern engineering teams deploy microservices in lightweight containers for environment parity.",
            "beginner_action": "Install Docker Desktop, pull an official Python or Alpine image, and run a test container interactively.",
            "practical_project": "Write a multi-stage Dockerfile and docker-compose.yml file that connects a backend web service to a PostgreSQL container.",
            "resource_title": "Official Docker Getting Started Guide",
            "resource_url": "https://docs.docker.com/get-started/",
            "estimated_effort": "8 - 12 hours (Estimated beginner curve)"
        },
        "Kubernetes": {
            "why_it_matters": "Orchestrates container deployment, scaling, health-checking, and zero-downtime rolling updates in production.",
            "beginner_action": "Enable Minikube or Docker Desktop Kubernetes and deploy a basic pod using `kubectl run`.",
            "practical_project": "Create Deployment and Service YAML manifests with replicas=2 and perform a rolling update via `kubectl apply`.",
            "resource_title": "Kubernetes Official Interactive Basics Tutorial",
            "resource_url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
            "estimated_effort": "15 - 20 hours (Estimated practice)"
        },
        "AWS": {
            "why_it_matters": "The leading cloud infrastructure provider; roles frequently demand cloud hosting, serverless, or storage knowledge.",
            "beginner_action": "Set up a free-tier AWS account, configure AWS CLI credentials, and launch a small t4g.nano EC2 instance.",
            "practical_project": "Deploy an S3 static site backed by CloudFront, or create an AWS Lambda function triggered by an API Gateway endpoint.",
            "resource_title": "AWS Cloud Essentials & Getting Started",
            "resource_url": "https://aws.amazon.com/getting-started/",
            "estimated_effort": "12 - 16 hours (Estimated practice)"
        },
        "PostgreSQL": {
            "why_it_matters": "The gold standard relational database for enterprise web apps requiring ACID guarantees and JSON indexing.",
            "beginner_action": "Install psql or pgAdmin, create a database schema with foreign keys, and write indexing queries.",
            "practical_project": "Design a relational schema with at least 4 tables, write complex JOIN queries, and analyze query execution using EXPLAIN ANALYZE.",
            "resource_title": "PostgreSQL Official Tutorial",
            "resource_url": "https://www.postgresql.org/docs/current/tutorial.html",
            "estimated_effort": "10 - 14 hours (Estimated practice)"
        },
        "CI/CD": {
            "why_it_matters": "Automates linting, test execution, security scans, and deployment pipelines to keep codebases production-ready.",
            "beginner_action": "Create a `.github/workflows/test.yml` file in a GitHub repository that runs pytest on every git push.",
            "practical_project": "Build an automated GitHub Actions pipeline that lints code, runs unit tests, builds a Docker image, and fails on coverage below 80%.",
            "resource_title": "GitHub Actions Quickstart & Docs",
            "resource_url": "https://docs.github.com/en/actions/quickstart",
            "estimated_effort": "6 - 10 hours (Estimated practice)"
        },
        "React": {
            "why_it_matters": "The dominant component-driven frontend library powering modern responsive user interfaces.",
            "beginner_action": "Follow the official tutorial using Vite (`npm create vite@latest`) to build an interactive component with useState.",
            "practical_project": "Build a responsive CRUD dashboard with search filtering, optimistic UI updates, and REST API integration.",
            "resource_title": "Official React Documentation (react.dev)",
            "resource_url": "https://react.dev/learn",
            "estimated_effort": "15 - 25 hours (Estimated practice)"
        },
        "TypeScript": {
            "why_it_matters": "Eliminates entire classes of runtime bugs through static typing and provides self-documenting codebases in team settings.",
            "beginner_action": "Convert a small JavaScript utility file to TypeScript by creating explicit interfaces and type aliases.",
            "practical_project": "Build a strictly typed REST client or schema validator using TypeScript generics and zod.",
            "resource_title": "TypeScript Official Handbook",
            "resource_url": "https://www.typescriptlang.org/docs/handbook/intro.html",
            "estimated_effort": "8 - 12 hours (Estimated practice)"
        },
        "Unit & Integration Testing": {
            "why_it_matters": "Demonstrates code quality discipline and prevents regressions in collaborative environments.",
            "beginner_action": "Write basic unit test assertions using pytest or Jest for 3 standalone helper functions.",
            "practical_project": "Implement comprehensive test coverage (>85%) with parameterized tests, fixtures, and API mocking for a backend service.",
            "resource_title": "pytest Official Getting Started Guide",
            "resource_url": "https://docs.pytest.org/en/stable/getting-started.html",
            "estimated_effort": "6 - 10 hours (Estimated practice)"
        },
        "RESTful APIs": {
            "why_it_matters": "Foundational architectural pattern for client-server communication across web, mobile, and third-party integrations.",
            "beginner_action": "Map out standard HTTP verbs (GET, POST, PUT, DELETE) and status codes (200, 201, 400, 404, 500) for a resource.",
            "practical_project": "Build a REST API adhering to OpenAPI specifications with request validation, structured error responses, and pagination.",
            "resource_title": "Mozilla MDN Web Docs: HTTP Overview",
            "resource_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview",
            "estimated_effort": "8 - 12 hours (Estimated practice)"
        },
        "FastAPI": {
            "why_it_matters": "High-performance Python web framework with asynchronous execution and automatic OpenAPI documentation.",
            "beginner_action": "Build a 'Hello World' FastAPI app with Pydantic query parameters and test the automatic `/docs` Swagger UI.",
            "practical_project": "Create an async API with authentication, background tasks, and dependency injection.",
            "resource_title": "FastAPI Official Tutorial",
            "resource_url": "https://fastapi.tiangolo.com/tutorial/",
            "estimated_effort": "8 - 12 hours (Estimated practice)"
        },
        "System Design": {
            "why_it_matters": "Essential for evaluating scalability, caching strategies, database sharding, and latency bottlenecks.",
            "beginner_action": "Study the difference between horizontal and vertical scaling and where caching fits in web architectures.",
            "practical_project": "Draft a system architecture diagram for an URL shortener handling 10M requests/day including cache and database layers.",
            "resource_title": "The System Design Primer (Open Source)",
            "resource_url": "https://github.com/donnemartin/system-design-primer",
            "estimated_effort": "20 - 30 hours (Estimated practice)"
        }
    }

    @classmethod
    def generate(
        cls,
        missing_skills: List[Dict[str, Any]],
        partial_skills: List[Dict[str, Any]],
        job_title: str = "Target Role"
    ) -> List[Dict[str, Any]]:
        """
        Creates a prioritized roadmap from missing and partial skills.
        Groups into: High Priority, Medium Priority, and Optional Improvements.
        """
        roadmap: List[Dict[str, Any]] = []

        # Process Missing Skills
        for item in missing_skills:
            skill_name = item.get("skill", "")
            req_type = item.get("type", "Required")
            
            # Missing Required skills are HIGH priority; Missing Preferred are MEDIUM/OPTIONAL
            priority = "High Priority" if req_type == "Required" else "Optional Improvement"
            priority_code = "high" if req_type == "Required" else "low"

            guidance = cls._get_guidance(skill_name, job_title)
            roadmap.append({
                "skill": skill_name,
                "category": item.get("category", "Technical"),
                "status": "Missing Evidence",
                "priority": priority,
                "priority_code": priority_code,
                "why_it_matters": guidance["why_it_matters"],
                "beginner_action": guidance["beginner_action"],
                "practical_project": guidance["practical_project"],
                "resource_title": guidance["resource_title"],
                "resource_url": guidance["resource_url"],
                "estimated_effort": guidance["estimated_effort"],
                "tag": "Skill Gap"
            })

        # Process Partial Skills
        for item in partial_skills:
            skill_name = item.get("skill", "")
            related = item.get("related_skill_found", "related tech")
            
            guidance = cls._get_guidance(skill_name, job_title)
            roadmap.append({
                "skill": skill_name,
                "category": item.get("category", "Technical"),
                "status": f"Partial Match (Familiar with {related})",
                "priority": "Medium Priority",
                "priority_code": "medium",
                "why_it_matters": f"You already have experience with {related}. Bridging to {skill_name} will make your profile complete for {job_title}.",
                "beginner_action": f"Compare {skill_name} syntax and idioms with {related}. Focus on architectural differences.",
                "practical_project": f"Port an existing small project built with {related} over to {skill_name}.",
                "resource_title": guidance["resource_title"],
                "resource_url": guidance["resource_url"],
                "estimated_effort": "4 - 8 hours (Accelerated by prior knowledge)",
                "tag": "Knowledge Bridge"
            })

        # Sort: High priority first, then Medium, then Low
        priority_order = {"high": 1, "medium": 2, "low": 3}
        roadmap.sort(key=lambda x: priority_order.get(x["priority_code"], 4))

        return roadmap

    @classmethod
    def _get_guidance(cls, skill_name: str, job_title: str) -> Dict[str, Any]:
        """Looks up curated guidance or synthesizes realistic guidance for unrecognized skills."""
        if skill_name in cls.CURATED_RESOURCES:
            return cls.CURATED_RESOURCES[skill_name]
        
        # Generic fallback for skills not in explicit curated dictionary
        return {
            "why_it_matters": f"Frequently referenced in job descriptions for {job_title} to demonstrate practical execution ability.",
            "beginner_action": f"Read the official documentation quickstart for {skill_name} and build a minimal proof-of-concept.",
            "practical_project": f"Create a working sample application or module that integrates {skill_name} into a GitHub repository.",
            "resource_title": f"Official Documentation & Community Tutorials for {skill_name}",
            "resource_url": "https://developer.mozilla.org/en-US/",  # MDN as standard trustworthy fallback
            "estimated_effort": "8 - 14 hours (Estimated practice)"
        }
