from flask import Flask
from datetime import datetime
from app.receive_experience import experience_bp
from duri_common.logger import get_logger

def create_app():
    app = Flask(__name__)
    logger = get_logger("evolution")
    logger.info("Evolution Flask 앱 초기화 완료")

    app.register_blueprint(experience_bp, url_prefix="/experience")

    @app.route("/health", methods=["GET"])
    def health_check():
        return {
            "status": "healthy",
            "service": "duri-evolution",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }

    return app
