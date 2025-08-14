#!/usr/bin/env python3
"""
DuRi Control API Server Runner
"""

import sys
import os
import uvicorn

# 프로젝트 루트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from duri_control.app import create_app
from duri_common.logger import get_logger

logger = get_logger("duri_control.run")

# FastAPI 앱 인스턴스 생성 (uvicorn에서 필요)
app = create_app()

def main():
    port = int(os.environ.get('PORT', 8083))

    try:
        logger.info("🎮 DuRi Control API 서버 시작 중...")
        logger.info(f"📍 포트: {port}")
        logger.info("=" * 50)

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )

    except Exception as e:
        logger.error(f"❌ Control 서버 시작 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
