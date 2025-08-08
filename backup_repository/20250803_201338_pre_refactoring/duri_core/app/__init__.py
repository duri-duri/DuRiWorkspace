#!/usr/bin/env python3
"""
DuRi Emotion API Flask Application
"""

import os
from flask import Flask
from duri_common.logger import get_logger
from duri_common.config.config import Config

logger = get_logger("duri_core.app")
app_config = Config()

def create_app():
    """Flask 앱 팩토리 함수"""
    app = Flask(__name__)
    
    # 환경변수 설정
    app.config['LOG_DIR'] = app_config.get_log_dir()
    app.config['RECEIVE_JSON_LOG'] = app_config.get_receive_json_log()
    app.config['BRAIN_URL'] = app_config.get_brain_url()
    app.config['EVOLUTION_URL'] = app_config.get_evolution_url()
    app.config['EVOLUTION_LOG_PATH'] = app_config.get_evolution_log()
    app.config['ACTION_STATS_PATH'] = app_config.get_action_stats_path()
    
    # 디렉토리 생성
    try:
        os.makedirs(app.config['LOG_DIR'], exist_ok=True)
    except Exception as e:
        logger.error(f"LOG_DIR 생성 실패: {e}")
        app.config['LOG_DIR'] = "/tmp/logs"
        os.makedirs(app.config['LOG_DIR'], exist_ok=True)
    
    try:
        os.makedirs(os.path.dirname(app.config['RECEIVE_JSON_LOG']), exist_ok=True)
    except Exception as e:
        logger.error(f"RECEIVE_JSON_LOG 디렉토리 생성 실패: {e}")
        app.config['RECEIVE_JSON_LOG'] = "/tmp/receive.json"
    
    # 액션 통계 디렉토리 생성
    try:
        os.makedirs(os.path.dirname(app.config['ACTION_STATS_PATH']), exist_ok=True)
    except Exception as e:
        logger.error(f"ACTION_STATS_PATH 디렉토리 생성 실패: {e}")
        app.config['ACTION_STATS_PATH'] = "/tmp/evolution_data/action_stats.json"
        os.makedirs(os.path.dirname(app.config['ACTION_STATS_PATH']), exist_ok=True)
    
    # 로그 파일 경로 설정
    app.config['LOG_FILE'] = os.path.join(app.config['LOG_DIR'], "emotion_receive.log")
    
    # 라우트 등록
    from duri_core.app.api import bp as api_bp
    app.register_blueprint(api_bp)
    
    logger.info("Flask 앱 초기화 완료")
    return app 
