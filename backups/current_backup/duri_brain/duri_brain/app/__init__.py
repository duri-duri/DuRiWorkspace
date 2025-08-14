from flask import Flask
from datetime import datetime
from .receive_decision_input import decision_input_bp
# from app.decide_action import decide_action_bp  # 필요 시 활성화

def create_app():
    app = Flask(__name__)
    app.register_blueprint(decision_input_bp, url_prefix="/decision_input")
    # app.register_blueprint(decide_action_bp, url_prefix="/decide_action")

    @app.route("/health", methods=["GET"])
    def health_check():
        return {
            "status": "healthy",
            "service": "duri-brain",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }

    return app
