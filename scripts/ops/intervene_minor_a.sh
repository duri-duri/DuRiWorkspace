#!/usr/bin/env bash
# 경미 개입 A: 변이·표본을 "조금만" 늘려 KS_p, unique_ratio 밀어 올림
# 그리드 탐색: DURI_24H_RECENT_WEIGHT ∈ {1.2, 1.3, 1.4}
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

WEIGHT_STATE_FILE="${WEIGHT_STATE_FILE:-.reports/synth/weight_grid_state.json}"

echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 경미 개입 A 시작"

# 1) 샘플 하한 확인 (이미 설정됨)
echo "[1] 샘플 하한 확인"
if docker compose config | grep -q "DURI_FORCE_MIN_SAMPLES=5"; then
    echo "  ✓ DURI_FORCE_MIN_SAMPLES=5 설정됨"
else
    echo "  ⚠ DURI_FORCE_MIN_SAMPLES 확인 필요"
fi

# 2) 단일 서비스 슬롯 재시드 (1회만)
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

# 3) 24h 가중치 그리드 탐색 (1.2, 1.3, 1.4)
echo "[3] 24h 가중치 그리드 탐색"
read_weight_state() {
    if [ -f "$WEIGHT_STATE_FILE" ]; then
        jq -r '.current_weight, .round_count, .last_ks_p' "$WEIGHT_STATE_FILE" 2>/dev/null || echo "1.3 0 0"
    else
        echo "1.3 0 0"
    fi
}

write_weight_state() {
    local weight="$1"
    local round="$2"
    local ks_p="$3"
    mkdir -p "$(dirname "$WEIGHT_STATE_FILE")"
    jq -n \
        --arg w "$weight" \
        --arg r "$round" \
        --arg k "$ks_p" \
        '{current_weight: ($w | tonumber), round_count: ($r | tonumber), last_ks_p: ($k | tonumber), tested_weights: [1.2, 1.3, 1.4], timestamp: now}' \
        > "$WEIGHT_STATE_FILE"
}

read -r current_weight round_count last_ks_p <<< "$(read_weight_state)"

# 안전장치: 상한 1.5 캡, 변동 0.1 이내
if (( $(echo "$current_weight > 1.5" | bc -l) )); then
    current_weight=1.5
fi

# 그리드 탐색: 1.2 → 1.3 → 1.4
if [ "$round_count" -eq 0 ]; then
    next_weight=1.2
elif [ "$round_count" -eq 1 ]; then
    next_weight=1.3
elif [ "$round_count" -eq 2 ]; then
    next_weight=1.4
else
    # 롤백 규칙: 3라운드 내 KS_p 중간값 상승 없으면 직전 값으로 롤백
    if [ "$round_count" -ge 3 ]; then
        current_ks_p=$(docker exec prometheus sh -lc "wget -qO- 'localhost:9090/api/v1/query?query=duri_p_uniform_ks_p'" 2>/dev/null | \
            jq -r '.data.result[]? | select(.metric.window=="24h") | .value[1]' 2>/dev/null || echo "0")
        if (( $(echo "$current_ks_p <= $last_ks_p" | bc -l) )); then
            echo "  ⚠ KS_p 미상승: $current_ks_p <= $last_ks_p"
            echo "  → 롤백: 직전 가중치로 복귀"
            next_weight=1.3  # 기본값으로 롤백
            round_count=0
        else
            echo "  ✓ KS_p 상승: $current_ks_p > $last_ks_p"
            next_weight=$current_weight  # 유지
        fi
    else
        next_weight=$current_weight
    fi
fi

# 가중치 적용 (환경변수 설정, 다음 실행에 반영)
export DURI_24H_RECENT_WEIGHT="$next_weight"
echo "  → 가중치 설정: DURI_24H_RECENT_WEIGHT=$next_weight"

# 현재 KS_p 읽기
current_ks_p=$(docker exec prometheus sh -lc "wget -qO- 'localhost:9090/api/v1/query?query=duri_p_uniform_ks_p'" 2>/dev/null | \
    jq -r '.data.result[]? | select(.metric.window=="24h") | .value[1]' 2>/dev/null || echo "0")

write_weight_state "$next_weight" "$((round_count + 1))" "$current_ks_p"

# 4) Exporter 재실행 (메트릭 갱신)
echo "[4] Exporter 재실행"
TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"
if [ -f "scripts/ops/p_sigma_export.py" ]; then
    DURI_24H_RECENT_WEIGHT="$next_weight" TEXTFILE_DIR="$TEXTFILE_DIR" python3 scripts/ops/p_sigma_export.py || true
fi
if [ -f "scripts/ops/p_uniform_ks.py" ]; then
    TEXTFILE_DIR="$TEXTFILE_DIR" python3 scripts/ops/p_uniform_ks.py || true
fi

echo "[COMPLETE] $(date +%Y-%m-%d\ %H:%M:%S)"
echo "  → 기대효과: ΔKS_p≈+0.05~0.08, Δunique_ratio≈+0.03~0.05"
echo "  → 다음 관찰: 30분 후 monitor_ab_gates.sh 재실행"
echo "  → 롤백 규칙: 3라운드 내 KS_p 미상승 시 직전 값으로 롤백"

