import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from app import create_app, init_db, db_session
from app.config import Config

class TestConfig(Config):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    UPLOAD_FOLDER = str(Path(__file__).parent / "test_uploads")
    GEMINI_API_KEY = "test_dummy_key_12345678"
    DEMO_MODE_DEFAULT = True

@pytest.fixture(scope="session")
def sample_pdf_path():
    path = Path("C:/Users/prata/.gemini/antigravity/scratch/resumeiq/sample_resumes/alex_chen_fullstack.pdf")
    assert path.exists(), f"Sample PDF missing at {path}"
    return str(path)

@pytest.fixture(scope="session")
def sample_docx_path():
    path = Path("C:/Users/prata/.gemini/antigravity/scratch/resumeiq/sample_resumes/sarah_miller_data_engineer.docx")
    assert path.exists(), f"Sample DOCX missing at {path}"
    return str(path)

@pytest.fixture
def app():
    app = create_app(TestConfig)
    upload_dir = Path(TestConfig.UPLOAD_FOLDER)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    with app.app_context():
        yield app
        if db_session:
            db_session.remove()

@pytest.fixture
def client(app):
    return app.test_client()
