#!/usr/bin/env bash
# Shadow/Legacy 경로 선택 헬퍼
# 사용법: CORE_DIR="$(pick_path duri_core)"

pick_path() {
  local want="$1"           # duri_core / duri_brain / ...
  local legacy="${want}_legacy"

  if [ -e "./${want}" ]; then
    echo "./${want}"
  else
    echo "./${legacy}"
  fi
}

# 사용 예시
# CORE_DIR="$(pick_path duri_core)"
# BRAIN_DIR="$(pick_path duri_brain)"
# EVOLUTION_DIR="$(pick_path duri_evolution)"
# CONTROL_DIR="$(pick_path duri_control)"
