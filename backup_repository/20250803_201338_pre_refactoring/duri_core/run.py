#!/usr/bin/env python3
"""
DuRi Core API Server Runner
"""

import sys
import os

# ✅ DuRiWorkspace 전체를 PYTHONPATH에 추가 (로컬/컨테이너 모두 대응)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from duri_common.logger import get_logger
from duri_common.config.config import Config

logger = get_logger("duri_core.run")
run_config = Config()

def main():
    app = create_app()
    port = 8080  # 고정 포트

    try:
        logger.info("🚀 DuRi Core 서버 시작 중...")
        logger.info(f"📍 포트: {port}")
        logger.info(f"📁 로그 디렉토리: {app.config['LOG_DIR']}")
        logger.info(f"📄 수신 로그: {app.config['RECEIVE_JSON_LOG']}")
        logger.info(f"🧠 Brain URL: {app.config['BRAIN_URL']}")
        logger.info(f"🔄 Evolution URL: {app.config['EVOLUTION_URL']}")
        logger.info("=" * 50)

        app.run(host="0.0.0.0", port=port, debug=False)

    except OSError as e:
        logger.error(f"❌ 포트 {port} 사용 실패: {e}")
        logger.error("⚠️ DuRi의 각 노드는 고정 포트를 사용해야 합니다. .env에서 포트를 다시 지정하세요.")
        exit(1)

if __name__ == "__main__":
    main()
