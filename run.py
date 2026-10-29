import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
    print(f"[*] Starting ResumeIQ on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=debug)
