"""
app.py
------
Main entry point for LaunchPad AI.

- Configures Flask + SQLAlchemy
- Exposes REST routes for analyzing startups and retrieving history
- Auto-launches an Ngrok tunnel so the app is reachable publicly
"""

import os
import json
import logging
from datetime import datetime

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from pyngrok import ngrok, conf

from services.ai_engine import generate_startup_analysis, AIEngineError

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("launchpad-ai")

MAX_INPUT_LENGTH = 2000
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'launchpad.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Database Model
# ---------------------------------------------------------------------------

class StartupReport(db.Model):
    __tablename__ = "startup_reports"

    id = db.Column(db.Integer, primary_key=True)
    startup_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.Text, nullable=False)
    business_model = db.Column(db.Text, nullable=False)

    viability_score = db.Column(db.Integer, nullable=False)
    innovation_score = db.Column(db.Integer, nullable=False)
    swot_json = db.Column(db.Text, nullable=False)          # stored as JSON string
    market_insights = db.Column(db.Text, nullable=False)
    growth_strategy = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "startup_name": self.startup_name,
            "description": self.description,
            "target_audience": self.target_audience,
            "business_model": self.business_model,
            "viability_score": self.viability_score,
            "innovation_score": self.innovation_score,
            "swot": json.loads(self.swot_json),
            "market_insights": self.market_insights,
            "growth_strategy": self.growth_strategy,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ---------------------------------------------------------------------------
# Validation Helpers
# ---------------------------------------------------------------------------

def validate_input(payload: dict):
    """
    Validates the incoming request payload.
    Returns (cleaned_data, None) on success, or (None, error_message) on failure.
    """
    required_fields = ["startup_name", "description", "target_audience", "business_model"]
    cleaned = {}

    if not isinstance(payload, dict):
        return None, "Invalid request format."

    for field in required_fields:
        value = payload.get(field, "")
        if value is None:
            value = ""
        value = str(value).strip()

        if not value:
            return None, f"Field '{field.replace('_', ' ')}' cannot be empty."

        if len(value) > MAX_INPUT_LENGTH:
            return None, f"Field '{field.replace('_', ' ')}' exceeds the {MAX_INPUT_LENGTH} character limit."

        cleaned[field] = value

    return cleaned, None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Renders the main dashboard."""
    return render_template("index.html", max_length=MAX_INPUT_LENGTH)


@app.route("/api/analyze", methods=["POST"])
def analyze_startup():
    """
    Accepts startup details as JSON, calls the AI engine, persists the
    report, and returns the structured analysis to the frontend.
    """
    payload = request.get_json(silent=True)
    cleaned, error = validate_input(payload)

    if error:
        return jsonify({"success": False, "error": error}), 400

    try:
        analysis = generate_startup_analysis(
            name=cleaned["startup_name"],
            description=cleaned["description"],
            audience=cleaned["target_audience"],
            business_model=cleaned["business_model"],
        )
    except AIEngineError as e:
        logger.error("AI engine error: %s", e)
        return jsonify({"success": False, "error": str(e)}), 502
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        return jsonify({"success": False, "error": "An unexpected server error occurred."}), 500

    try:
        report = StartupReport(
            startup_name=cleaned["startup_name"],
            description=cleaned["description"],
            target_audience=cleaned["target_audience"],
            business_model=cleaned["business_model"],
            viability_score=analysis["viability_score"],
            innovation_score=analysis["innovation_score"],
            swot_json=json.dumps(analysis["swot"]),
            market_insights=analysis["market_insights"],
            growth_strategy=analysis["growth_strategy"],
        )
        db.session.add(report)
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Failed to persist report to database")
        # Analysis succeeded even if persistence failed; still return the result
        return jsonify({"success": True, "data": analysis, "warning": "Report generated but not saved to history."})

    return jsonify({"success": True, "data": report.to_dict()})


@app.route("/api/history", methods=["GET"])
def get_history():
    """Returns the most recent saved reports (newest first)."""
    try:
        reports = StartupReport.query.order_by(StartupReport.created_at.desc()).limit(20).all()
        return jsonify({"success": True, "data": [r.to_dict() for r in reports]})
    except Exception:
        logger.exception("Failed to fetch history")
        return jsonify({"success": False, "error": "Could not retrieve history."}), 500


@app.route("/api/history/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    """Deletes a single saved report."""
    report = StartupReport.query.get(report_id)
    if not report:
        return jsonify({"success": False, "error": "Report not found."}), 404
    try:
        db.session.delete(report)
        db.session.commit()
        return jsonify({"success": True})
    except Exception:
        db.session.rollback()
        logger.exception("Failed to delete report")
        return jsonify({"success": False, "error": "Could not delete report."}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Resource not found."}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error."}), 500


# ---------------------------------------------------------------------------
# Ngrok Tunnel Setup
# ---------------------------------------------------------------------------

def start_ngrok_tunnel(port: int):
    """
    Authenticates with Ngrok using NGROK_AUTHTOKEN and opens a public tunnel
    to the local Flask server. Prints the public URL to the terminal.
    """
    authtoken = os.environ.get("NGROK_AUTHTOKEN")

    if not authtoken or authtoken == "your_ngrok_authtoken_here":
        logger.warning(
            "NGROK_AUTHTOKEN not set in .env — skipping tunnel creation. "
            "The app will still run locally at http://127.0.0.1:%s", port
        )
        return None

    try:
        conf.get_default().auth_token = authtoken
        tunnel = ngrok.connect(port, "http")
        public_url = tunnel.public_url
        logger.info("=" * 60)
        logger.info(" LaunchPad AI is LIVE")
        logger.info(" Local:  http://127.0.0.1:%s", port)
        logger.info(" Public: %s", public_url)
        logger.info("=" * 60)
        return tunnel
    except Exception as e:
        logger.error("Failed to start Ngrok tunnel: %s", e)
        logger.warning("Continuing with local server only at http://127.0.0.1:%s", port)
        return None


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        logger.info("Database tables ensured.")

    PORT = int(os.environ.get("PORT", 5000))

    start_ngrok_tunnel(PORT)

    # debug=False is required so the Flask reloader does not spawn a second
    # process, which would open a duplicate (and conflicting) Ngrok tunnel.
    app.run(host="0.0.0.0", port=PORT, debug=False)
