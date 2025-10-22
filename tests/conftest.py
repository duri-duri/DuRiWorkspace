# tests/conftest.py
import os

# 테스트 실행 시에는 DB 연결을 강제로 스킵하도록 지시
# (duri_core.core.database가 아래 키들을 True로 해석하면 연결을 건너뛰게 수정하는게 베스트)
os.environ.setdefault("DURI_DB_SKIP", "1")
os.environ.setdefault("DURI_TEST_SKIP_DB", "1")
os.environ.setdefault("DURICORE_SKIP_DB", "1")
