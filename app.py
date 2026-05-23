"""Application entrypoint. Run with `python app.py`."""
import eventlet
eventlet.monkey_patch()  # noqa: E402  must run before other imports

import os
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import socketio, init_mongo
from api.auth import auth_bp
from api.datasets import datasets_bp
from api.reports import reports_bp
from api.automl import automl_bp
from api.visualizations import viz_bp
from sockets.training import register_training_namespace
from utils.errors import register_error_handlers


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_UPLOAD_MB * 1024 * 1024

    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}}, supports_credentials=True)

    init_mongo(Config.MONGO_URI, Config.MONGO_DB)

    # Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(datasets_bp, url_prefix="/api/datasets")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(automl_bp, url_prefix="/api/automl")
    app.register_blueprint(viz_bp, url_prefix="/api/datasets")  # nested under dataset id

    register_error_handlers(app)

    @app.get("/")
    def health():
         return {"message": "API is running"}

    socketio.init_app(app)
    register_training_namespace(socketio)
    return app


app = create_app()


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=Config.PORT, debug=Config.ENV == "development")
