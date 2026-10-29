from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Metadata
    candidate_name = Column(String(150), default="Candidate")
    resume_filename = Column(String(255), nullable=False)
    job_title = Column(String(200), nullable=True)
    company_name = Column(String(200), nullable=True)
    has_job_description = Column(Boolean, default=False, nullable=False)
    
    # Quantitative Indicators (Transparently calculated)
    job_match_score = Column(Float, nullable=True)     # 0 - 100
    ats_readiness_score = Column(Float, nullable=False) # 0 - 100
    
    # Mode and audit
    is_demo_mode = Column(Boolean, default=False, nullable=False)
    model_used = Column(String(100), default="heuristic-demo", nullable=False)
    
    # Text summaries & cached metrics for fast listing
    summary = Column(Text, nullable=False)
    key_strengths = Column(Text, nullable=True)    # JSON string array
    key_gaps = Column(Text, nullable=True)         # JSON string array
    
    # Full comprehensive payload
    full_report_json = Column(Text, nullable=False)

    def to_summary_dict(self):
        """Returns concise summary for history listings and comparison tables."""
        strengths = []
        gaps = []
        try:
            if self.key_strengths:
                strengths = json.loads(self.key_strengths)
        except Exception:
            strengths = []
            
        try:
            if self.key_gaps:
                gaps = json.loads(self.key_gaps)
        except Exception:
            gaps = []

        return {
            "id": self.id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M UTC") if self.created_at else "",
            "candidate_name": self.candidate_name,
            "resume_filename": self.resume_filename,
            "job_title": self.job_title or "General Evaluation (No JD)",
            "company_name": self.company_name or "N/A",
            "has_job_description": self.has_job_description,
            "job_match_score": round(self.job_match_score, 1) if self.job_match_score is not None else None,
            "ats_readiness_score": round(self.ats_readiness_score, 1) if self.ats_readiness_score is not None else 0,
            "is_demo_mode": self.is_demo_mode,
            "model_used": self.model_used,
            "summary": self.summary,
            "key_strengths": strengths[:4],
            "key_gaps": gaps[:4]
        }

    def to_full_dict(self):
        """Returns the full report payload."""
        try:
            report_data = json.loads(self.full_report_json)
        except Exception:
            report_data = {}

        data = self.to_summary_dict()
        data["report"] = report_data
        return data
