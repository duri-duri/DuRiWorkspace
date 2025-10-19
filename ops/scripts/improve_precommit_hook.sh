#!/usr/bin/env bash
set -euo pipefail

# pre-commit 훅 개선 스크립트
# duri-smoke 훅 실패 시 빠른 재현 및 디버깅을 위한 도구

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
cd "$PROJECT_DIR"

echo "=== pre-commit 훅 개선 도구 ==="

# 1) 현재 훅 상태 확인
echo "**1) 현재 pre-commit 훅 확인:**"
if [ -f ".pre-commit-config.yaml" ]; then
    echo "✅ .pre-commit-config.yaml 존재"
    grep -A 5 -B 5 "duri-smoke" .pre-commit-config.yaml || echo "⚠️ duri-smoke 훅 없음"
else
    echo "❌ .pre-commit-config.yaml 없음"
fi

# 2) smoke_check.sh 실행 가능성 확인
echo -e "\n**2) smoke_check.sh 실행 가능성 확인:**"
if [ -f "ops/scripts/smoke_check.sh" ]; then
    echo "✅ smoke_check.sh 존재"
    chmod +x ops/scripts/smoke_check.sh
    echo "✅ 실행 권한 설정"
    
    # 문법 검사
    if bash -n ops/scripts/smoke_check.sh; then
        echo "✅ 문법 검사 통과"
    else
        echo "❌ 문법 오류 발견"
        exit 1
    fi
else
    echo "❌ smoke_check.sh 없음"
    exit 1
fi

# 3) 로컬 smoke 테스트 (Prometheus 없이)
echo -e "\n**3) 로컬 smoke 테스트:**"
echo "Prometheus가 실행 중인지 확인..."
if curl -sf http://localhost:9090/-/ready >/dev/null 2>&1; then
    echo "✅ Prometheus 실행 중 - 전체 테스트 실행"
    bash ops/scripts/smoke_check.sh
else
    echo "⚠️ Prometheus 미실행 - 문법만 검사"
    echo "전체 테스트를 위해서는 다음 명령어로 Prometheus를 시작하세요:"
    echo "bash ops/scripts/one_shot_start.sh"
fi

# 4) 훅 개선 제안
echo -e "\n**4) 훅 개선 제안:**"
cat << 'EOF'

.pre-commit-config.yaml에 다음 추가 권장:

- repo: local
  hooks:
    - id: duri-smoke
      name: DuRi Smoke Test
      entry: bash ops/scripts/smoke_check.sh
      language: system
      pass_filenames: false
      always_run: false
      stages: [pre-commit]

또는 더 안전한 버전:

- repo: local
  hooks:
    - id: duri-smoke
      name: DuRi Smoke Test
      entry: bash -c 'set -euo pipefail; bash ops/scripts/smoke_check.sh || { echo "[duri-smoke] smoke_check failed"; exit 1; }'
      language: system
      pass_filenames: false
      always_run: false
      stages: [pre-commit]

EOF

echo "=== 완료 ==="
