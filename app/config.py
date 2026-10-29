import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "resumeiq-academic-secret-key-2026-safe-dev")
    DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
    
    # Upload settings
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "uploads_temp"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))  # 5 MB
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    
    # Database
    DATABASE_PATH = BASE_DIR / "instance" / "resumeiq.db"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini AI
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()
    GEMINI_TIMEOUT_SECONDS = int(os.environ.get("GEMINI_TIMEOUT_SECONDS", 25))
    
    # Demo Mode Override (can be forced via env or toggled in UI session)
    DEMO_MODE_DEFAULT = os.environ.get("DEMO_MODE", "False").lower() in ("true", "1", "yes")
