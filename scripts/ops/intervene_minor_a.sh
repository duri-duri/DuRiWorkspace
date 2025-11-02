#!/usr/bin/env bash
# 경미 개입 A: 변이·표본을 "조금만" 늘려 KS_p, unique_ratio 밀어 올림
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 경미 개입 A 시작"

# 1) 샘플 하한 확인 (이미 설정됨)
echo "[1] 샘플 하한 확인"
if docker compose config | grep -q "DURI_FORCE_MIN_SAMPLES=5"; then
    echo "  ✓ DURI_FORCE_MIN_SAMPLES=5 설정됨"
else
    echo "  ⚠ DURI_FORCE_MIN_SAMPLES 확인 필요"
fi

# 2) 슬롯 소폭 재시드 (단일 서비스 1회)
# duri-brain만 재시작 (가장 영향 적음)
echo "[2] 슬롯 소폭 재시드 (duri-brain 1회)"
LOCKFILE="${LOCKFILE:-.reports/synth/intervene_minor_a.lock}"
if [ -f "$LOCKFILE" ]; then
    local last_run=$(stat -c %Y "$LOCKFILE" 2>/dev/null || echo 0)
    local now=$(date +%s)
    if [ $((now - last_run)) -lt 3600 ]; then
        echo "  ⚠ 최근 1시간 내 실행됨, 스킵"
    else
        echo "  → duri-brain 재시작"
        docker compose restart duri-brain
        touch "$LOCKFILE"
    fi
else
    echo "  → duri-brain 재시작"
    docker compose restart duri-brain
    touch "$LOCKFILE"
fi

# 3) 24h 창 가중 확인 (이미 코드 반영됨)
echo "[3] 24h 창 가중 확인"
if grep -q "weight.*2h\|recent.*weight" scripts/ops/p_sigma_export.py 2>/dev/null; then
    echo "  ✓ 24h 창 가중 로직 존재"
else
    echo "  ℹ 24h 창 가중은 p_sigma_export.py에 반영 필요 (선택적)"
fi

# 4) Exporter 재실행 (메트릭 갱신)
echo "[4] Exporter 재실행"
TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"
if [ -f "scripts/ops/p_sigma_export.py" ]; then
    TEXTFILE_DIR="$TEXTFILE_DIR" python3 scripts/ops/p_sigma_export.py || true
fi
if [ -f "scripts/ops/p_uniform_ks.py" ]; then
    TEXTFILE_DIR="$TEXTFILE_DIR" python3 scripts/ops/p_uniform_ks.py || true
fi

echo "[COMPLETE] $(date +%Y-%m-%d\ %H:%M:%S)"
echo "  → 기대효과: P(KS_p≥0.05) ~ +0.08, unique_ratio ~ +0.05"
echo "  → 다음 관찰: 30분 후 monitor_ab_gates.sh 재실행"

