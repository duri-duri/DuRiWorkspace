#!/usr/bin/env bash
# 24h 파일럿 실행 스크립트 (HTTP-only, 10분 주기)
# 자동 롤백 규칙 포함

set -Eeuo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin"

cd /home/duri/DuRiWorkspace

# PID 락 (중복 루프 방지)
LOCK=/tmp/pilot_24h.lock
exec 9>"$LOCK"
if ! flock -n 9; then
    echo "[LOCK] already running (PID: $(pgrep -f pilot_24h.sh | head -1))" >&2
    exit 0
fi

# 필수 명령 확인 (PATH 고정 + 필수 바이너리 보장)
for c in curl awk jq bash python3; do
  command -v "$c" >/dev/null || { echo "[MISS] $c" >&2; exit 127; }
done

# last_age 헬퍼
last_age() {
  curl -fsS localhost:9109/metrics 2>/dev/null | \
    awk '/^duri_last_ev_unixtime/{t=$2} END{now=systime(); print now-int(t)}' || echo "999999"
}

# 누락 함수 보강
dump_bash_state() {
    set +e
    echo "== bash state =="
    type -a bash >/dev/null 2>&1 || true
    env | sort | head -20
    set -e
}

# 옵션 파싱
ONE_SHOT=0
if [[ "${1:-}" == "--one-shot" ]]; then
    ONE_SHOT=1
fi

# 환경 변수 설정
export ALLOW_SHADOW_NONINTERACTIVE=1
unset ALLOW_READYFAIL  # 진짜 readiness로
mkdir -p .shadow && : > .shadow/ALLOW_RUN
mkdir -p var/run

# SSH 비율 초기화 (조건부 유지)
HTTP_OK=0
SSH_OK=0

# 모니터링 함수
check_ev_velocity() {
    local ev_1h=$(find var/evolution -maxdepth 1 -type d -name 'EV-*' -newermt '-1 hour' 2>/dev/null | wc -l)
    local ev_24h=$(find var/evolution -maxdepth 1 -type d -name 'EV-*' -newermt '-24 hours' 2>/dev/null | wc -l)
    echo "[1h] $ev_1h EV  |  [24h] $ev_24h EV"
}

# 최근 EV 목록 (find -printf 사용, ls -lt 대체)
list_recent_ev() {
    find var/evolution -maxdepth 1 -type d -name 'EV-*' -printf '%T@ %f\n' 2>/dev/null | sort -nr | head -3 | awk '{print $2}'
}

check_no_new_ev() {
    local ev_time=$(curl -fsS localhost:9109/metrics 2>/dev/null | awk '/^duri_last_ev_unixtime/{print $2;exit}' || echo "0")
    if [ "$ev_time" != "0" ]; then
        local now=$(date +%s)
        local diff=$(python3 -c "import sys; print(int(sys.argv[1]) - int(float(sys.argv[2])))" "$now" "$ev_time" 2>/dev/null || echo "999999")
        echo "Δt=${diff}s"
        if [ "$diff" -gt 1800 ]; then
            echo "[PREALERT] Δt > 1800s (롤백 임계값의 25%, 목표 Δt95에 근접)"
        fi
        if [ "$diff" -gt 7200 ]; then
            echo "[ROLLBACK] Δt > 7200s (2h 초과)"
            return 1
        fi
    fi
    return 0
}

check_pvalue_drift() {
    local ph=$(curl -fsS localhost:9109/metrics 2>/dev/null | awk '/^duri_ab_p_value[[:space:]]/{print $2;exit}' || echo "0")
    local pf=$(awk '/^duri_ab_p_value[[:space:]]/{print $2;exit}' var/metrics/ab_eval.prom 2>/dev/null || echo "0")
    if [ "$ph" != "0" ] && [ "$pf" != "0" ]; then
        local drift=$(python3 -c "import sys,math; ph=float(sys.argv[1]); pf=float(sys.argv[2]); d=abs(ph-pf); print(d)" "$ph" "$pf" 2>/dev/null || echo "999")
        if (( $(echo "$drift <= 0.000000001" | bc -l 2>/dev/null || awk -v d="$drift" 'BEGIN{if (d <= 0.000000001) print 1; else print 0}') )); then
            echo "OK drift (HTTP=$ph FILE=$pf)"
            return 0
        else
            echo "DRIFT $drift (HTTP=$ph FILE=$pf)"
            return 1
        fi
    fi
    return 0
}

check_exporter_health() {
    local exporter_up=$(curl -fsS localhost:9109/metrics 2>/dev/null | awk '/^duri_shadow_exporter_up[[:space:]]/{print $2;exit}' || echo "0")
    # exporter_up=1.0 또는 1은 정상
    if [ "$exporter_up" = "1" ] || [ "$exporter_up" = "1.0" ] || (( $(echo "$exporter_up >= 1" | bc -l 2>/dev/null || awk -v v="$exporter_up" 'BEGIN{if (v >= 1) print 1; else print 0}') )); then
        rm -f var/run/exporter_down_start 2>/dev/null || true
        return 0
    else
        # exporter_up==0 지속 시간 확인 (간단 버전)
        if [ -f var/run/exporter_down_start ]; then
            local down_start=$(cat var/run/exporter_down_start)
            local now=$(date +%s)
            local down_duration=$((now - down_start))
            if [ "$down_duration" -ge 300 ]; then
                echo "[ROLLBACK] exporter_up=$exporter_up ≥300s 지속"
                return 1
            fi
        else
            echo "$(date +%s)" > var/run/exporter_down_start
        fi
        echo "[WARN] exporter_up=$exporter_up (비정상, 300s 지속 시 롤백)"
        return 1
    fi
}

# 롤백 체크 (즉시 중단)
check_rollback_conditions() {
    echo "[$(date)] 롤백 조건 체크..."
    
    # 1. Δt(마지막 EV) > 7200s (2h)
    if ! check_no_new_ev; then
        echo "[ROLLBACK] 조건 1: 마지막 EV > 2h 초과"
        return 1
    fi
    
    # 2. drift > 1e-9 2회 연속 (이전 값과 비교 필요하므로 간단 체크)
    local drift_count=0
    if ! check_pvalue_drift; then
        drift_count=1
        # 이전 drift 상태 확인 (파일로 저장)
        if [ -f var/run/pvalue_drift_fail ]; then
            echo "[ROLLBACK] 조건 2: p-value drift > 1e-9 2회 연속"
            return 1
        else
            echo "d" > var/run/pvalue_drift_fail
        fi
    else
        rm -f var/run/pvalue_drift_fail 2>/dev/null || true
    fi
    
    # 3. exporter_up==0가 5분 이상 지속 (간단 체크)
    if ! check_exporter_health; then
        echo "[ROLLBACK] 조건 3: exporter_up 비정상 5분 이상"
        return 1
    fi
    
    return 0
}

# 메인 루프
echo "[$(date)] 24h 파일럿 시작 (HTTP-only, 10분 주기 × 144회)"
echo "[INFO] 롤백 조건: Δt>2h, drift>1e-9 2회 연속, exporter_up==0 5분 이상"
echo "[INFO] 최적화: 주기 압축(30분→10분), HTTP-only, 런당 EV 보장"

# 프리-알람이면 바로 보정 버스트
AGE="$(last_age)"
if [ -n "$AGE" ] && [ "$AGE" -gt 1800 ] && [ "$ONE_SHOT" -eq 0 ]; then
    echo "[pilot] pre-alert Δt_now=${AGE}s → corrective burst"
    bash "$0" --one-shot || true
fi

# SSH 비율 설정 (1/8, 조건부 유지)
: "${DURI_SSH_RATIO:=1/8}"
SSH_RATIO_DENOM=8  # 8회 중 1회 SSH

# 파일럿 생존 가드 (죽어있으면 재기동)
_pilot_guard() {
    if ! pgrep -f pilot_24h.sh >/dev/null 2>&1; then
        echo "[GUARD] 파일럿 프로세스 없음 → 재기동"
        nohup bash scripts/pilot_24h.sh >> var/logs/pilot_24h.log 2>&1 &
        sleep 2
    fi
}

# 프리-알람 체크 (Δt>1800s, 임계값 하향)
check_prealert() {
    local ev_time=$(curl -fsS localhost:9109/metrics 2>/dev/null | awk '/^duri_last_ev_unixtime/{print $2;exit}' || echo "0")
    if [ "$ev_time" != "0" ]; then
        local now=$(date +%s)
        local diff=$(python3 -c "import sys; print(int(sys.argv[1]) - int(float(sys.argv[2])))" "$now" "$ev_time" 2>/dev/null || echo "999999")
        if [ "$diff" -gt 1800 ]; then
            echo "[PREALERT] Δt>1800s (현재: ${diff}s, 롤백 임계값: 7200s, 목표 Δt95: ≤1800s)"
            return 1
        fi
    fi
    return 0
}

# SSH 유지 조건 체크
check_ssh_maintain() {
    # HTTP 6h 연속 OK && SSH 각 서비스 3연속 OK
    # 간단 버전: HTTP 최근 12회(6h) OK && SSH 최근 3회 OK
    local http_ok_count=0
    local ssh_ok_count=0
    
    # 최근 로그에서 성공 여부 확인 (간단 버전)
    if [ -f var/logs/pilot_24h.log ]; then
        http_ok_count=$(tail -100 var/logs/pilot_24h.log 2>/dev/null | grep -c "HTTP.*OK\|HTTP.*완료" || echo "0")
        ssh_ok_count=$(tail -100 var/logs/pilot_24h.log 2>/dev/null | grep -c "SSH.*OK\|SSH.*완료" || echo "0")
    fi
    
    # 조건: HTTP 12회 이상 && SSH 3회 이상
    if [ "$http_ok_count" -ge 12 ] && [ "$ssh_ok_count" -ge 3 ]; then
        return 0  # SSH 유지
    else
        return 1  # HTTP only
    fi
}

for i in {1..144}; do  # 144회 × 10분 = 1440분 (24h)
    echo ""
    echo "[$(date)] === Run $i/144 ===" 
    
    # 파일럿 생존 가드
    _pilot_guard
    
    # 롤백 조건 체크
    if ! check_rollback_conditions; then
        echo "[$(date)] 롤백 조건 충족 → 파일럿 중단"
        exit 1
    fi
    
    # 프리-알람 체크 (임계값 하향: 3600s → 1800s)
    if ! check_prealert; then
        echo "[WARN] 프리-알람: Δt>1800s (롤백 임계값의 25%, 목표 Δt95에 근접)"
    fi
    
    # 모니터링 출력
    echo "[MONITOR] $(check_ev_velocity)"
    echo "[MONITOR] $(check_no_new_ev)"
    check_pvalue_drift && echo "[MONITOR] p-value drift OK" || echo "[MONITOR] p-value drift 경고"
    check_exporter_health && echo "[MONITOR] exporter_up OK" || echo "[MONITOR] exporter_up 경고"
    
    # HTTP 실행 (HTTP-only 고정, SSH 비활성)
    export TRANSPORT=http
    export DURI_SSH_RATIO="0/1"  # SSH 비활성화
    echo "[$(date)] HTTP 트리거 시작 (HTTP-only, 주기 10분)..."
    if timeout 300 bash scripts/shadow_duri_integration_final.sh; then
        HTTP_OK=$((HTTP_OK + 1))
    else
        echo "[WARN] HTTP 실행 경고"
        HTTP_OK=0  # 연속 성공 카운터 리셋
    fi
    
    # SSH 비활성화 (파일럿 최적화)
    # SSH 비율 적용 비활성화 (HTTP-only 정책)
    
    # B) in-flight 가드 튜닝: MAX_INFLIGHT=4, -mmin -9, MAX_GAP_SEC=300
    MIN_GAP_SEC=480   # 8m
    MAX_GAP_SEC=300   # 9m (상한 간격 10m → 9m로 축소)
    : "${MAX_INFLIGHT:=6}"
    LAST_TS_FILE=var/run/last_ev_unixtime
    
    if [ $i -lt 144 ]; then  # 144회 × 8-10분 = 1152-1440분 (19-24h 범위)
        now=$(date +%s)
        last=$(cat "$LAST_TS_FILE" 2>/dev/null || echo 0)
        gap=$((now - last))
        
        # B) in-flight 가드: 워커2 + 파일럿1의 겹침 허용, 실제 주기 8-12m라면 9분 창
        mkdir -p var/run
        inflight=$(find var/evolution -maxdepth 1 -type d -name "EV-*" -mmin -9 2>/dev/null | wc -l)
        
        # 간격 가드: 최소 간격 미달 시 스킵
        if [ "$gap" -lt "$MIN_GAP_SEC" ] && [ "$last" -ne 0 ]; then
            wait_time=$((MIN_GAP_SEC - gap))
            echo "[$(date)] SKIP: gap=${gap}s < ${MIN_GAP_SEC}s, ${wait_time}s 대기 후 재시도"
            sleep "$wait_time"
        # in-flight 가드: 동시 실행 중인 EV 수 초과 시 스킵
        elif [ "$inflight" -ge "$MAX_INFLIGHT" ]; then
            echo "[$(date)] SKIP: inflight=${inflight} >= ${MAX_INFLIGHT}, 대기 중..."
            sleep 60
        else
            # 8-12분 랜덤 대기 (평균 10분)
            sleep_time=$((480 + (RANDOM % 241)))  # 480-720초
            echo "[$(date)] ${sleep_time}s 대기 중... ($(($i*sleep_time/60))분 경과, gap=${gap}s, inflight=${inflight})"
            sleep "$sleep_time"
        fi
    fi
done

echo ""
echo "[$(date)] === 24h 파일럿 완료 ==="
echo "[FINAL] 최종 모니터링:"
check_ev_velocity
check_no_new_ev
check_pvalue_drift
check_exporter_health

