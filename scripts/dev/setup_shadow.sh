#!/usr/bin/env bash
# Shadow 훈련장 설정 스크립트 (로컬 전용)
# 사용법: bash scripts/dev/setup_shadow.sh

set -euxo pipefail

BASE="${HOME}/DuRiShadow"
mkdir -p "${BASE}"

clone_or_pull() {
  local name="$1"
  local repo="$2"

  if [ -d "${BASE}/${name}/.git" ]; then
    echo "🔄 ${name} 업데이트 중..."
    git -C "${BASE}/${name}" remote set-url origin "git@github.com:duri-duri/${repo}.git" || true
    git -C "${BASE}/${name}" fetch --all -p
    git -C "${BASE}/${name}" checkout main
    git -C "${BASE}/${name}" pull --ff-only
  else
    echo "📥 ${name} 클론 중..."
    git clone "git@github.com:duri-duri/${repo}.git" "${BASE}/${name}"
  fi

  # 심볼릭 링크 생성
  ln -sfn "${BASE}/${name}" "./${name}"
  echo "✅ ${name} 링크 생성 완료"
}

echo "🎯 Shadow 훈련장 설정 시작..."
echo "📍 Shadow 디렉토리: ${BASE}"

clone_or_pull duri_core      duri_core
clone_or_pull duri_brain     duri_brain
clone_or_pull duri_evolution duri_evolution
clone_or_pull duri_control   duri_control

echo ""
echo "✅ Shadow 훈련장 준비 완료!"
echo ""
echo "📋 Shadow 링크 확인:"
ls -l duri_core duri_brain duri_evolution duri_control
