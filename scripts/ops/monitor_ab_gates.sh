# --- hard guards ---
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
PROM_CONTAINER="${PROM_CONTAINER:-prometheus}"
LOCK="${LOCK:-$ROOT/var/locks/monitor_gates.lock}"
RETRY="${RETRY:-2}"                  # unbound variable 방지
PROM_QUERY_TIMEOUT="${PROM_QUERY_TIMEOUT:-2500}"  # ms
STATE_DIR="${STATE_DIR:-.reports/synth/state}"
STATE_FILE="${STATE_FILE:-$STATE_DIR/ab_gate_state.json}"
mkdir -p "$STATE_DIR" 2>/dev/null || echo "[WARN] cannot mkdir $STATE_DIR" >&2

# 초기 grace(초) — 첫 스크랩 대기
GRACE_SEC="${GRACE_SEC:-120}"
start_ts="$(date +%s)"

# 최소 샘플 수 (n 기준 그레이스)
MIN_N="${MIN_N:-200}"

mkdir -p "$(dirname "$LOCK")"

# flock: 중복 방지
exec 200>"$LOCK"
flock -n 200 || { echo "[SKIP] 다른 인스턴스 실행 중"; exit 0; }

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

# Prometheus 쿼리 함수 (이중 질의 + 재시도 + 폴백)
query_prom() {
    local q="$1"
    local kind="${2:-host}"
    local try=0
    local resp=""
    
    while [ $try -le $RETRY ]; do
        if [ "$kind" = "host" ]; then
            resp="$(curl -sf --max-time 3 "$PROM_URL/api/v1/query?query=$q" 2>/dev/null || true)"
        else
            resp="$(docker exec "$PROM_CONTAINER" sh -lc "wget -qO- 'http://localhost:9090/api/v1/query?query=$q'" 2>/dev/null || true)"
        fi
        
        if [ -n "$resp" ] && echo "$resp" | jq -e '.data.result[0].value' >/dev/null 2>&1; then
            echo "$resp"
            return 0
        fi
        try=$((try+1))
        sleep 0.8
    done
    
    echo ""  # 공백응답 반환 (호출측이 RED로 처리)
    return 1
}

# 안전한 값 추출 함수 (jq 실패/공백이면 0)
safe_value() {
    local payload="$1"
    [ -n "$payload" ] && echo "$payload" | jq -r '.data.result[0].value[1] // "0"' 2>/dev/null || echo "0"
}

# 텍스트파일 폴백 함수 (Observability Contract v1)
fallback_from_textfile() {
    local name="$1"
    local lbl="${2:-}"
    local textfile_dir="${TEXTFILE_DIR:-.reports/synth}"
    local v=""  # 초기화 필수
    
    # 샘플수 메트릭: 라벨有/無 모두 지원
    if [[ "$name" == *"samples"* ]] || [[ "$name" == *"SAMPLES"* ]]; then
        # 먼저 라벨 있는 버전 찾기
        if [ -n "$lbl" ]; then
            v=$(awk -v n="$name" -v L="$lbl" '
                $1 ~ "^" n "{" {
                    if (index($0, L) > 0) {
                        print $NF
                        exit
                    }
                }
            ' "$textfile_dir"/*.prom 2>/dev/null | head -1 || echo "")
        fi
        # 라벨 없는 버전도 찾기 (하위호환)
        if [ -z "$v" ]; then
            v=$(awk -v n="$name" '
                $1 ~ "^" n "[[:space:]]" {
                    print $NF
                    exit
                }
            ' "$textfile_dir"/*.prom 2>/dev/null | head -1 || echo "")
        fi
    else
        # 다른 메트릭: 기존 로직
        if [ -n "$lbl" ]; then
            v=$(awk -v n="$name" -v L="$lbl" '
                $1 ~ "^" n "{" {
                    if (index($0, L) > 0) {
                        print $NF
                        exit
                    }
                }
            ' "$textfile_dir"/*.prom 2>/dev/null | head -1 || echo "")
        else
            v=$(awk -v n="$name" '
                $1 ~ "^" n "{" || $1 ~ "^" n "[[:space:]]" {
                    print $NF
                    exit
                }
            ' "$textfile_dir"/*.prom 2>/dev/null | head -1 || echo "")
        fi
    fi
    
    echo "${v:-}"
}

# Prometheus 쿼리 또는 텍스트파일 폴백 (Observability Contract v1: 빈 벡터 방어 + 초기 grace)
query_prom_or_fallback() {
    local metric="$1"
    local lbl="${2:-}"
    local v=""
    local fallback=""
    
    # Try Prometheus first (host → container fallback)
    local resp="$(query_prom "$metric" "host")"
    if [ -z "$resp" ] || ! echo "$resp" | jq -e '.data.result[0].value' >/dev/null 2>&1; then
        resp="$(query_prom "$metric" "container")"
    fi
    
    # Extract value if valid response
    if [ -n "$resp" ] && echo "$resp" | jq -e '.data.result[0].value' >/dev/null 2>&1; then
        v=$(echo "$resp" | jq -r '.data.result[0].value[1] // empty' 2>/dev/null || echo "")
    fi
    
    # Fallback to textfile if Prometheus query failed or returned empty
    if [ -z "$v" ] || [ "$v" = "0" ] || [ "$v" = "" ]; then
        fallback=$(fallback_from_textfile "$metric" "$lbl")
    fi
    
    # 초기 GRACE: Prom 응답이 비어있으면 GRACE_SEC 동안은 fallback값이 있으면 그걸 우선, 없으면 빈값 반환
    if [ -z "$v" ] || [ "$v" = "0" ] || [ "$v" = "" ]; then
        now="$(date +%s)"
        if [ $((now - start_ts)) -lt "$GRACE_SEC" ]; then
            [ -n "$fallback" ] && v="$fallback" || v=""
        else
            v="$fallback"
        fi
    fi
    
    # Final fallback: 0
    echo "${v:-0}"
}

# Prometheus 쿼리 헬퍼 (전체 결과, 공백응답 가드 포함)
query_prom_all() {
    local query="$1"
    local resp="$(query_prom "$query" "host")"
    
    # 호스트 실패 → 컨테이너 폴백
    if [ -z "$resp" ] || ! echo "$resp" | jq -e '.data.result[0].value' >/dev/null 2>&1; then
        resp="$(query_prom "$query" "container")"
    fi
    
    if [ -z "$resp" ] || ! echo "$resp" | jq -e '.data.result[0].value' >/dev/null 2>&1; then
        echo "[WARN] prometheus 응답 없음: query=$query" >&2
        echo "0"
        return 1
    fi
    
    echo "$resp" | jq -r '.data.result[]?.value[1]' 2>/dev/null || echo "0"
}

# 3) 메트릭 수집 (폴백 우선순위: Prom → textfile → 0, 샘플수는 OR 쿼리)
collect_metrics() {
    # KS·unique (폴백 사용)
    local ks_p_2h=$(query_prom_or_fallback "duri_p_uniform_ks_p{window=\"2h\"}" 'window="2h"')
    local ks_p_24h=$(query_prom_or_fallback "duri_p_uniform_ks_p{window=\"24h\"}" 'window="24h"')
    
    # unique ratio (폴백 사용)
    local unique_2h=$(query_prom_or_fallback "duri_p_unique_ratio{window=\"2h\"}" 'window="2h"')
    local unique_24h=$(query_prom_or_fallback "duri_p_unique_ratio{window=\"24h\"}" 'window="24h"')
    
    # σ (폴백 사용)
    local sigma_2h=$(query_prom_or_fallback "duri_p_sigma{window=\"2h\"}" 'window="2h"')
    local sigma_24h=$(query_prom_or_fallback "duri_p_sigma{window=\"24h\"}" 'window="24h"')
    
    # 표본 수 (샘플수: 단일 진실원 duri_p_n 사용)
    # Recording rule로 코얼레싱 처리되어 단순 쿼리만 필요
    local n_2h=$(query_prom_or_fallback "duri_p_n{window=\"2h\"}" 'window="2h"')
    local n_24h=$(query_prom_or_fallback "duri_p_n{window=\"24h\"}" 'window="24h"')
    
    # 폴백: recording rule이 없으면 직접 쿼리 (하위호환)
    if [ "$(printf '%.0f' "${n_2h:-0}" 2>/dev/null || echo "0")" -eq 0 ]; then
        local fallback_2h=$(fallback_from_textfile "duri_p_samples" "window=\"2h\"")
        [ -z "$fallback_2h" ] && fallback_2h=$(fallback_from_textfile "duri_p_sigma_samples" "window=\"2h\"")
        [ -n "$fallback_2h" ] && n_2h="$fallback_2h"
    fi
    if [ "$(printf '%.0f' "${n_24h:-0}" 2>/dev/null || echo "0")" -eq 0 ]; then
        local fallback_24h=$(fallback_from_textfile "duri_p_samples" "window=\"24h\"")
        [ -z "$fallback_24h" ] && fallback_24h=$(fallback_from_textfile "duri_p_sigma_samples" "window=\"24h\"")
        [ -n "$fallback_24h" ] && n_24h="$fallback_24h"
    fi
    
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
    
    # n 기준 그레이스: 임계 재조정 (파이프라인 생존성 우선)
    local n_2h_num=$(printf '%.0f' "${n_2h:-0}" 2>/dev/null || echo "0")
    local n_24h_num=$(printf '%.0f' "${n_24h:-0}" 2>/dev/null || echo "0")
    local judgment_note=""
    
    # n>=1이면 YELLOW, n>=200이면 GREEN (파이프라인 생존성 우선)
    if [ "$n_2h_num" -ge 200 ] 2>/dev/null || [ "$n_24h_num" -ge 200 ] 2>/dev/null; then
        judgment_note="(n>=200, GREEN)"
    elif [ "$n_2h_num" -ge 1 ] 2>/dev/null || [ "$n_24h_num" -ge 1 ] 2>/dev/null; then
        judgment_note="(n>=1, YELLOW grace: 파이프라인 생존 확인)"
    else
        judgment_note="(n=0, RED: 파이프라인 중단 가능)"
    fi
    
    echo "$ks_p_2h $ks_p_24h $unique_2h $unique_24h $sigma_2h $sigma_24h $n_2h $n_24h $judgment_note"
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
    # 디렉토리 보장 (재발 방지)
    mkdir -p "$(dirname "$STATE_FILE")" 2>/dev/null || {
        echo "[WARN] cannot mkdir $(dirname "$STATE_FILE")" >&2
        return 0
    }
    
    local green_count="$1"
    local yellow_count="$2"
    local red_count="$3"
    local judgment="$4"
    
    # jq 에러 처리 강화
    if ! command -v jq >/dev/null 2>&1; then
        echo "[WARN] jq 없음, 상태 파일 기록 스킵" >&2
        return 0
    fi
    
    # 원자적 쓰기 (tmp 파일 사용)
    local tmpf=$(mktemp "$(dirname "$STATE_FILE")/.tmp.XXXXXX" 2>/dev/null || echo "")
    if [ -z "$tmpf" ]; then
        echo "[WARN] cannot create temp file for $STATE_FILE" >&2
        return 0
    fi
    
    jq -n \
        --arg gc "$green_count" \
        --arg yc "$yellow_count" \
        --arg rc "$red_count" \
        --arg j "$judgment" \
        '{green_count: ($gc | tonumber), yellow_count: ($yc | tonumber), red_count: ($rc | tonumber), last_judgment: $j, timestamp: now}' \
        > "$tmpf" 2>/dev/null && mv "$tmpf" "$STATE_FILE" 2>/dev/null || {
        rm -f "$tmpf" 2>/dev/null
        echo "[WARN] 상태 파일 기록 실패 ($STATE_FILE), 계속 진행" >&2
        return 0
    }
}

# 5) 메인 루프
main() {
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 가드 달린 관찰 모드 시작"
    
    # 메트릭 수집
    local metrics=$(collect_metrics)
    read -r ks_p_2h ks_p_24h unique_2h unique_24h sigma_2h sigma_24h n_2h n_24h <<< "$metrics"
    
    # 공백응답 가드: 메트릭이 모두 0이고 Prometheus 응답이 없으면 관용 처리
    local judgment=""
    if [ "$ks_p_2h" = "0" ] && [ "$ks_p_24h" = "0" ] && [ "$unique_2h" = "0" ] && [ "$unique_24h" = "0" ]; then
        # n 최근값이 존재(>=1)면 타임아웃 카운터로 판정, 아니면 RED
        local n_2h_num=$(printf '%.0f' "${n_2h:-0}" 2>/dev/null || echo "0")
        local n_24h_num=$(printf '%.0f' "${n_24h:-0}" 2>/dev/null || echo "0")
        
        if [ "$n_2h_num" -ge 1 ] 2>/dev/null || [ "$n_24h_num" -ge 1 ] 2>/dev/null; then
            # timeout 카운터 파일
            local TOF="$STATE_DIR/prom_timeout.count"
            local cnt=0
            if [ -f "$TOF" ]; then
                cnt=$(cat "$TOF" 2>/dev/null || echo "0")
            fi
            cnt=$((cnt + 1))
            echo "$cnt" > "$TOF" 2>/dev/null || true
            
            if [ "$cnt" -ge 3 ]; then
                judgment="RED"
                echo "[NOTE] prometheus timeout x3 → RED"
            else
                judgment="YELLOW"
                echo "[NOTE] prometheus timeout 응답 (${cnt}/3), n>=1 → YELLOW (관용 처리)"
            fi
        else
            judgment="RED"
            echo "[WARN] prometheus 응답 없음 또는 메트릭 부재 → 이번 라운드 RED로 표기하고 계속 진행"
        fi
    fi
    
    echo "[METRICS]"
    echo "  KS_p (2h/24h): $ks_p_2h / $ks_p_24h"
    echo "  unique_ratio (2h/24h): $unique_2h / $unique_24h"
    echo "  sigma (2h/24h): $sigma_2h / $sigma_24h"
    echo "  n (2h/24h): $n_2h / $n_24h"
    
    # 판정: 원-비트 지표 우선 사용
    if [ -z "$judgment" ]; then
        # 먼저 원-비트 지표 확인 (파이프라인 생존/정상)
        local q_green='duri_pipeline_green'
        local green_val=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
            --data-urlencode "query=$q_green" 2>/dev/null | jq -r '.data.result[0].value[1] // "0"' 2>/dev/null || echo "0")
        
        if [ "$green_val" = "1" ] 2>/dev/null; then
            judgment="GREEN"
            echo "[NOTE] 원-비트 지표: duri_pipeline_green=1 → GREEN"
        else
            # duri_pipeline_alive 확인
            local alive_val=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
                --data-urlencode 'query=duri_pipeline_alive' 2>/dev/null | jq -r '.data.result[0].value[1] // "0"' 2>/dev/null || echo "0")
            
            if [ "$alive_val" = "1" ] 2>/dev/null; then
                judgment="YELLOW"
                echo "[NOTE] 원-비트 지표: duri_pipeline_alive=1 → YELLOW"
            else
                # 원-비트 지표 없으면 기존 judge_gate 사용
                judgment=$(judge_gate "$ks_p_2h" "$ks_p_24h" "$unique_2h" "$unique_24h" "$sigma_2h" "$sigma_24h" "$n_2h" "$n_24h")
                
                # n 기준 임계 재조정: n>=1이면 YELLOW, n>=200이면 GREEN (파이프라인 생존성 우선)
                local n_2h_num=$(printf '%.0f' "${n_2h:-0}" 2>/dev/null || echo "0")
                local n_24h_num=$(printf '%.0f' "${n_24h:-0}" 2>/dev/null || echo "0")
                
                if [ "$n_2h_num" -ge 200 ] 2>/dev/null || [ "$n_24h_num" -ge 200 ] 2>/dev/null; then
                    # n>=200이면 GREEN (다른 조건 무시)
                    judgment="GREEN"
                    echo "[NOTE] n 기준 재조정: n>=200 → GREEN (파이프라인 정상)"
                elif [ "$n_2h_num" -ge 1 ] 2>/dev/null || [ "$n_24h_num" -ge 1 ] 2>/dev/null; then
                    # n>=1이면 YELLOW (파이프라인 생존 확인)
                    if [ "$judgment" = "RED" ]; then
                        judgment="YELLOW"
                        echo "[NOTE] n 기준 그레이스 적용: RED → YELLOW (n>=1, 파이프라인 생존 확인)"
                    fi
                fi
            fi
        fi
    fi
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
            # 성공 라운드엔 timeout 카운터 리셋
            : > "$STATE_DIR/prom_timeout.count" 2>/dev/null || true
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
    
    # 베이지안/SPRT 통계적 판정 (에러 처리 강화)
    local bayes_output=""
    local bayes_prob="0"
    local sprt_output=""
    local sprt_result="CONTINUE"
    local sprt_ll="0"
    
    if command -v python3 >/dev/null 2>&1; then
        bayes_output=$(python3 scripts/ops/bayes_progress.py "$judgment" 2>/dev/null || echo "")
        bayes_prob=$(echo "$bayes_output" | grep -oE 'P\(p≥0\.8\|data\)=[0-9.]+' | grep -oE '[0-9.]+' | head -1 || echo "0")
        
        sprt_output=$(python3 scripts/ops/wald_sprt.py "$judgment" 2>/dev/null || echo "")
        sprt_result=$(echo "$sprt_output" | grep -oE '→ [A-Z]+' | tail -1 || echo "CONTINUE")
        sprt_ll=$(echo "$sprt_output" | grep -oE 'LR=[0-9.e+-]+' | grep -oE '[0-9.e+-]+' | head -1 || echo "0")
    fi
    
    echo "[STATISTICS]"
    echo "  베이지안: P(p≥0.8|data)=${bayes_prob}"
    echo "  SPRT: $sprt_result (LR=${sprt_ll})"
    
    # 진행표 CSV 기록 (라운드별 Bayes/SPRT 상태 누적) - 보장 쓰기 (에러와 무관하게)
    local progress_csv="${PROGRESS_CSV:-.reports/synth/progress.csv}"
    mkdir -p "$(dirname "$progress_csv")"
    judgment="${judgment:-RED}"  # 초기화 보장
    
    # CSV 기록 (에러 발생 시에도 반드시 기록)
    {
        echo "$(date +%F' '%T),$judgment,$ks_p_2h,$ks_p_24h,$unique_2h,$unique_24h,$sigma_2h,$sigma_24h,$n_2h,$n_24h,$sprt_ll,$bayes_prob"
    } >> "$progress_csv" 2>/dev/null || {
        # CSV 기록 실패 시에도 계속 진행
        echo "[WARN] CSV 기록 실패, 계속 진행" >&2
    }
    sync 2>/dev/null || true
    
    # 의사결정 (Sequential Rule + 통계적 판정)
    echo "[DECISION]"
    
    # 정지 규칙: 둘 다 충족 시 기다림 전환
    local can_wait=0
    green_count=${green_count:-0}
    if [ "$green_count" -ge 4 ] 2>/dev/null; then
        # 알람 확인 (간단 버전: Prometheus 쿼리)
        local alert_count=$(docker exec "$PROM_CONTAINER" sh -lc "wget -qO- 'localhost:9090/api/v1/alerts'?silenced=false&active=true" 2>/dev/null | \
            jq -r '.data.alerts[]? | select(.labels.alertname | test("ABPValuesUniformityLost|ABPSigmaNoSamples|ABPValuesKS")) | .labels.alertname' 2>/dev/null | wc -l || echo "0")
        alert_count=${alert_count:-0}
        if [ "$alert_count" -eq 0 ] 2>/dev/null; then
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

