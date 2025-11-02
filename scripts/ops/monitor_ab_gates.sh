#!/usr/bin/env bash
# 가드 달린 관찰 모드: Green/Yellow/Red 판정 및 자동 의사결정
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_CONTAINER="${PROM_CONTAINER:-prometheus}"
STATE_FILE="${STATE_FILE:-.reports/synth/ab_gate_state.json}"

# 1) 판정 함수
judge_gate() {
    local ks_p_2h="$1"
    local ks_p_24h="$2"
    local unique_2h="$3"
    local unique_24h="$4"
    local sigma_2h="$5"
    local sigma_24h="$6"
    local n_2h="$7"
    local n_24h="$8"
    
    # Green: unique_ratio≥0.30 AND KS_p≥0.05 AND σ>0 AND n≥12
    local green=0
    if (( $(echo "$unique_2h >= 0.30" | bc -l) )) && \
       (( $(echo "$unique_24h >= 0.30" | bc -l) )) && \
       (( $(echo "$ks_p_2h >= 0.05" | bc -l) )) && \
       (( $(echo "$ks_p_24h >= 0.05" | bc -l) )) && \
       (( $(echo "$sigma_2h > 0" | bc -l) )) && \
       (( $(echo "$sigma_24h > 0" | bc -l) )) && \
       (( $(echo "$n_2h >= 12" | bc -l) )) && \
       (( $(echo "$n_24h >= 12" | bc -l) )); then
        green=1
    fi
    
    # Red: unique_ratio<0.20 OR KS_p<0.01 OR n<5 OR σ=0
    local red=0
    if (( $(echo "$unique_2h < 0.20" | bc -l) )) || \
       (( $(echo "$unique_24h < 0.20" | bc -l) )) || \
       (( $(echo "$ks_p_2h < 0.01" | bc -l) )) || \
       (( $(echo "$ks_p_24h < 0.01" | bc -l) )) || \
       (( $(echo "$n_2h < 5" | bc -l) )) || \
       (( $(echo "$n_24h < 5" | bc -l) )) || \
       (( $(echo "$sigma_2h == 0" | bc -l) )) || \
       (( $(echo "$sigma_24h == 0" | bc -l) )); then
        red=1
    fi
    
    # Yellow: (0.20≤unique_ratio<0.30 OR 0.01≤KS_p<0.05) AND NOT Red
    local yellow=0
    if [ "$red" -eq 0 ]; then
        if (( $(echo "$unique_2h >= 0.20 && $unique_2h < 0.30" | bc -l) )) || \
           (( $(echo "$unique_24h >= 0.20 && $unique_24h < 0.30" | bc -l) )) || \
           (( $(echo "$ks_p_2h >= 0.01 && $ks_p_2h < 0.05" | bc -l) )) || \
           (( $(echo "$ks_p_24h >= 0.01 && $ks_p_24h < 0.05" | bc -l) )); then
            yellow=1
        fi
    fi
    
    if [ "$green" -eq 1 ]; then
        echo "GREEN"
    elif [ "$red" -eq 1 ]; then
        echo "RED"
    elif [ "$yellow" -eq 1 ]; then
        echo "YELLOW"
    else
        echo "UNKNOWN"
    fi
}

# 2) Prometheus 쿼리 함수 (정확한 쿼리 형식)
query_prom() {
    local query="$1"
    local window="$2"
    docker exec "$PROM_CONTAINER" sh -lc "wget -qO- 'localhost:9090/api/v1/query?query=$query'" 2>/dev/null | \
        jq -r ".data.result[]? | select(.metric.window==\"$window\") | .value[1]" 2>/dev/null || echo "0"
}

# Prometheus 쿼리 헬퍼 (전체 결과)
query_prom_all() {
    local query="$1"
    docker exec "$PROM_CONTAINER" sh -lc "wget -qO- 'localhost:9090/api/v1/query?query=$query'" 2>/dev/null | \
        jq -r '.data.result[]?.value[1]' 2>/dev/null || echo "0"
}

# 3) 메트릭 수집 (정확한 쿼리 형식)
collect_metrics() {
    # KS·unique
    local ks_p_results=$(query_prom_all "duri_p_uniform_ks_p")
    local ks_p_2h=$(echo "$ks_p_results" | head -1)
    local ks_p_24h=$(echo "$ks_p_results" | tail -1)
    
    # unique ratio
    local unique_results=$(query_prom_all "duri_p_unique_ratio")
    local unique_2h=$(echo "$unique_results" | head -1)
    local unique_24h=$(echo "$unique_results" | tail -1)
    
    # σ
    local sigma_results=$(query_prom_all "duri_p_sigma")
    local sigma_2h=$(echo "$sigma_results" | head -1)
    local sigma_24h=$(echo "$sigma_results" | tail -1)
    
    # 표본 수
    local n_results=$(query_prom_all "duri_p_samples")
    local n_2h=$(echo "$n_results" | head -1)
    local n_24h=$(echo "$n_results" | tail -1)
    
    # NaN/empty/null 처리
    ks_p_2h=${ks_p_2h:-0}
    ks_p_24h=${ks_p_24h:-0}
    unique_2h=${unique_2h:-0}
    unique_24h=${unique_24h:-0}
    sigma_2h=${sigma_2h:-0}
    sigma_24h=${sigma_24h:-0}
    n_2h=${n_2h:-0}
    n_24h=${n_24h:-0}
    
    # 숫자 변환 (NaN 문자열 처리)
    ks_p_2h=$(echo "$ks_p_2h" | grep -E "^[0-9.e+-]+$" || echo "0")
    ks_p_24h=$(echo "$ks_p_24h" | grep -E "^[0-9.e+-]+$" || echo "0")
    
    echo "$ks_p_2h $ks_p_24h $unique_2h $unique_24h $sigma_2h $sigma_24h $n_2h $n_24h"
}

# 4) 상태 파일 관리
read_state() {
    if [ -f "$STATE_FILE" ]; then
        jq -r '.green_count, .yellow_count, .red_count, .last_judgment' "$STATE_FILE" 2>/dev/null || echo "0 0 0 UNKNOWN"
    else
        echo "0 0 0 UNKNOWN"
    fi
}

write_state() {
    mkdir -p "$(dirname "$STATE_FILE")"
    local green_count="$1"
    local yellow_count="$2"
    local red_count="$3"
    local judgment="$4"
    jq -n \
        --arg gc "$green_count" \
        --arg yc "$yellow_count" \
        --arg rc "$red_count" \
        --arg j "$judgment" \
        '{green_count: ($gc | tonumber), yellow_count: ($yc | tonumber), red_count: ($rc | tonumber), last_judgment: $j, timestamp: now}' \
        > "$STATE_FILE"
}

# 5) 메인 루프
main() {
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 가드 달린 관찰 모드 시작"
    
    # 메트릭 수집
    local metrics=$(collect_metrics)
    read -r ks_p_2h ks_p_24h unique_2h unique_24h sigma_2h sigma_24h n_2h n_24h <<< "$metrics"
    
    echo "[METRICS]"
    echo "  KS_p (2h/24h): $ks_p_2h / $ks_p_24h"
    echo "  unique_ratio (2h/24h): $unique_2h / $unique_24h"
    echo "  sigma (2h/24h): $sigma_2h / $sigma_24h"
    echo "  n (2h/24h): $n_2h / $n_24h"
    
    # 판정
    local judgment=$(judge_gate "$ks_p_2h" "$ks_p_24h" "$unique_2h" "$unique_24h" "$sigma_2h" "$sigma_24h" "$n_2h" "$n_24h")
    echo "[JUDGMENT] $judgment"
    
    # 상태 읽기
    local state=$(read_state)
    read -r green_count yellow_count red_count last_judgment <<< "$state"
    
    # 카운트 업데이트
    case "$judgment" in
        GREEN)
            green_count=$((green_count + 1))
            yellow_count=0
            red_count=0
            ;;
        YELLOW)
            yellow_count=$((yellow_count + 1))
            red_count=0
            ;;
        RED)
            red_count=$((red_count + 1))
            ;;
    esac
    
    write_state "$green_count" "$yellow_count" "$red_count" "$judgment"
    
    # 베이지안/SPRT 통계적 판정
    local bayes_prob=$(python3 scripts/ops/bayes_progress.py "$judgment" 2>/dev/null | grep -oE 'P\(p≥0\.8\|data\)=[0-9.]+' | grep -oE '[0-9.]+' | head -1 || echo "0")
    local sprt_result=$(python3 scripts/ops/wald_sprt.py "$judgment" 2>/dev/null | grep -oE '→ [A-Z]+' | tail -1 || echo "CONTINUE")
    
    echo "[STATISTICS]"
    echo "  베이지안: P(p≥0.8|data)=${bayes_prob}"
    echo "  SPRT: $sprt_result"
    
    # 의사결정 (Sequential Rule + 통계적 판정)
    echo "[DECISION]"
    
    # 정지 규칙: 둘 다 충족 시 기다림 전환
    local can_wait=0
    if [ "$green_count" -ge 4 ]; then
        # 알람 확인 (간단 버전: Prometheus 쿼리)
        local alert_count=$(docker exec "$PROM_CONTAINER" sh -lc "wget -qO- 'localhost:9090/api/v1/alerts'?silenced=false&active=true" 2>/dev/null | \
            jq -r '.data.alerts[]? | select(.labels.alertname | test("ABPValuesUniformityLost|ABPSigmaNoSamples|ABPValuesKS")) | .labels.alertname' 2>/dev/null | wc -l || echo "0")
        if [ "$alert_count" -eq 0 ]; then
            can_wait=1
        fi
    fi
    
    bayes_prob_num=$(echo "$bayes_prob" | grep -oE '[0-9.]+' | head -1 || echo "0")
    if [ "$can_wait" -eq 1 ] && (( $(echo "$bayes_prob_num >= 0.8" | bc -l 2>/dev/null || echo "0") )); then
        echo "  → 완전 관찰 모드 전환 (정지 규칙 충족)"
        echo "  → 개입 중단"
        echo "  → 조건: Green 4회 연속 + 알람 무 + P(p≥0.8|data)≥0.8"
        echo "  → 증거 수집을 '수동 개입 없이' 지속"
    elif [ "$judgment" = "GREEN" ] && [ "$green_count" -ge 4 ]; then
        echo "  → Green 4회 연속 (베이지안/SPRT 확인 중)"
        echo "  → 계속 관찰"
    elif [ "$judgment" = "YELLOW" ] && [ "$yellow_count" -ge 3 ]; then
        echo "  → 경미 개입 A 실행 필요 (Yellow ≥3회)"
        echo "  → 실행: bash scripts/ops/intervene_minor_a.sh"
        echo "  → 기대효과: ΔKS_p≈+0.05~0.08, Δunique_ratio≈+0.03~0.05"
    elif [ "$judgment" = "RED" ]; then
        echo "  → 즉시 트리아지 실행 (Red 1회)"
        echo "  → 실행: bash scripts/ops/triage_red.sh"
        echo "  → 10분 컷: Exporter 산출물 → 규칙 검증 → 타깃 확인 → 워크스페이스 테스트"
    else
        echo "  → 계속 관찰 (현재: $judgment, 연속: $green_count/$yellow_count/$red_count)"
    fi
    
    echo "[COMPLETE] $(date +%Y-%m-%d\ %H:%M:%S)"
}

main "$@"

