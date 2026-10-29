import os
from pathlib import Path
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .config import Config
from .models.analysis import Base

# Database session factory
engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)
db_session = scoped_session(SessionLocal)

def init_db(app):
    global engine
    db_path = app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///instance/resumeiq.db")
    
    # Ensure instance directory exists
    instance_dir = Path(app.root_path).parent / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)
    
    engine = create_engine(db_path, connect_args={"check_same_thread": False})
    SessionLocal.configure(bind=engine)
    Base.metadata.create_all(bind=engine)
    return db_session

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    # Ensure uploads directory exists
    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    # Initialize Database
    session = init_db(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if db_session:
            db_session.remove()

    # Register Blueprints
    from .routes.main import main_bp
    from .routes.api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("base.html", error_title="Page Not Found", error_message="The requested page could not be located."), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "success": False,
            "error": "File size exceeds the 5MB limit. Please upload a smaller document."
        }), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": "An internal server error occurred. Please try again or check settings."
        }), 500

    return app
