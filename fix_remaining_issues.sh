#!/usr/bin/env bash
# 남은 문제 3가지 한 번에 해결 스크립트
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YEL='\033[1;33m'; NC='\033[0m'
pass(){ echo -e "${GREEN}✔ $*${NC}"; }
fail(){ echo -e "${RED}✘ $*${NC}"; exit 1; }
note(){ echo -e "${YEL}➜ $*${NC}"; }

cd /home/duri/DuRiWorkspace

echo "=== 남은 문제 3가지 해결 시작 ==="

# 1) /metrics 라우트 추가
note "1. /metrics 라우트 추가"
cat > duri_core/app/metrics.py << 'EOF'
#!/usr/bin/env python3
"""
Prometheus metrics endpoint for DuRi Core
"""
from flask import Blueprint, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

metrics_bp = Blueprint("metrics", __name__)

@metrics_bp.route("/metrics")
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
EOF

# 기존 app/__init__.py에 metrics_bp 등록
if ! grep -q "from .metrics import metrics_bp" duri_core/app/__init__.py; then
    sed -i '/from duri_core.app.metrics import metrics_bp, init_metrics/a\
from duri_core.app.metrics import metrics_bp' duri_core/app/__init__.py
fi

if ! grep -q "app.register_blueprint(metrics_bp)" duri_core/app/__init__.py; then
    sed -i '/app.register_blueprint(api_bp)/a\
app.register_blueprint(metrics_bp)' duri_core/app/__init__.py
fi

pass "metrics 라우트 추가 완료"

# 2) pyc 파일 추적 완전 제거
note "2. pyc 파일 추적 완전 제거"
cd duri_core
git rm -r --cached core/__pycache__/ 2>/dev/null || true
git rm --cached '*.pyc' 2>/dev/null || true
git add .gitignore
git commit -m "chore: purge tracked __pycache__ and pyc files

- Remove all tracked __pycache__/ and *.pyc files from Git
- Ensure .gitignore prevents future pyc file tracking"
cd ..
pass "pyc 파일 추적 제거 완료"

# 3) .dockerignore 보강
note "3. .dockerignore 보강"
cat > .dockerignore << 'EOF'
# Python
**/__pycache__/
**/*.pyc
**/*.pyo
**/*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment
.env
.venv
venv/

# Git
.git/
.gitignore
EOF
pass ".dockerignore 보강 완료"

# 4) 컨테이너 재빌드 및 재시작
note "4. 컨테이너 재빌드 및 재시작"
docker compose -p duriworkspace build duri-core
docker compose -p duriworkspace up -d duri-core
sleep 10
pass "컨테이너 재빌드 및 재시작 완료"

# 5) 검증
note "5. 검증"
echo "5-1) pyc 추적 확인:"
cd duri_core
pyc_count=$(git ls-files '*.pyc' | wc -l)
if [[ "$pyc_count" -eq 0 ]]; then
    pass "pyc 파일 추적 완전 제거됨 (0개)"
else
    fail "pyc 파일이 여전히 추적됨 ($pyc_count개)"
fi
cd ..

echo "5-2) /metrics 엔드포인트 확인:"
for i in 1 2 3; do
    if curl -fsS http://localhost:8080/metrics >/dev/null 2>&1; then
        pass "/metrics 엔드포인트 정상 동작"
        break
    fi
    if [[ $i -eq 3 ]]; then
        fail "/metrics 엔드포인트 여전히 실패"
    fi
    echo "  재시도 $i/3..."
    sleep $((i*2))
done

echo "5-3) 게이트 스크립트 테스트:"
if ./scripts/verify_gate_shadow.sh; then
    pass "게이트 스크립트 정상 통과"
else
    fail "게이트 스크립트 실패"
fi

echo ""
echo "=== 🎉 모든 문제 해결 완료! ==="
echo "✅ /metrics 라우트 추가됨"
echo "✅ pyc 파일 추적 완전 제거됨"
echo "✅ .dockerignore 보강됨"
echo "✅ 게이트 스크립트 정상 통과"
echo ""
echo "이제 게이트 전체가 완전히 매끈해졌습니다! 🚀"
