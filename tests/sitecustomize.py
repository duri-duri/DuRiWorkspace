# tests/sitecustomize.py
import os

# 혹시 스크립트에서 환경변수 세팅을 깜박해도, 테스트 경로에서는 무조건 스킵
os.environ.setdefault("DURI_DB_SKIP", "1")
os.environ.setdefault("DURI_TEST_SKIP_DB", "1")
os.environ.setdefault("DURICORE_SKIP_DB", "1")

# 테스트 환경임을 명시
os.environ.setdefault("DURI_TEST_MODE", "1")
