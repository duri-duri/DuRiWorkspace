import os
import sys

import uvicorn

# ✅ DuRiWorkspace 전체를 PYTHONPATH에 추가 (로컬/컨테이너 모두 대응)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

if __name__ == "__main__":
    port = 8081  # 고정 포트
    uvicorn.run(app, host="0.0.0.0", port=port)
