#!/usr/bin/env bash
set -Eeuo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin"

cd /home/duri/DuRiWorkspace

# --- hard guards --- (PATH 고정 + 필수 바이너리 보장)
for c in curl awk jq bash python3; do
  command -v "$c" >/dev/null || { echo "[MISS] $c" >&2; exit 127; }
done

# dump_bash_state 전역 보호 (no-op 가드)
command -v dump_bash_state >/dev/null 2>&1 || dump_bash_state(){ :; }

# dump helper (로컬 호출에서도 항상 존재)
dump_bash_state() {
  set +e
  echo "== bash/env state =="
  echo "SHELL=$SHELL"
  type -a bash 2>/dev/null || true
  env | sort | head -20
  set -e
}

# 모든 외부 실행을 감싸서 127/엑싯코드 로깅
run() {
  echo "[RUN] $*" >&2
  if ! "$@"; then
    rc=$?
    echo "[ERR] rc=$rc cmd=$*" >&2
    if [ $rc -eq 127 ]; then
      echo "[HINT] PATH=$PATH" >&2
      dump_bash_state
    fi
    return $rc
  fi
}

# ==========================================
# Shadow 훈련장 시작 - 안전장치 및 초기화
# ==========================================

# ==== SAFEGUARD: never run from CI or non-interactive unless explicitly allowed ====
if [[ -n "${CI:-}" || -n "${GITHUB_ACTIONS:-}" ]]; then
  echo "[SAFEGUARD] CI 환경에서 shadow 스크립트 실행 차단"
  exit 0
fi
if [[ ! -t 0 && "${ALLOW_SHADOW_NONINTERACTIVE:-0}" != "1" ]]; then
  echo "[SAFEGUARD] 비대화형 실행 차단 (ALLOW_SHADOW_NONINTERACTIVE=1 로 해제 가능)"
  exit 0
fi
# 선택: 승인 플래그가 없는 경우 차단
APPROVAL_FLAG=".shadow/ALLOW_RUN"
if [[ ! -f "$APPROVAL_FLAG" ]]; then
  echo "[SAFEGUARD] 승인 플래그($APPROVAL_FLAG) 없음 → 실행 차단"
  exit 0
fi

# 하이브리드 전송 어댑터 로드 (HTTP/SSH 선택적 사용)
source scripts/lib/transport.sh 2>/dev/null || {
    echo "[WARNING] transport.sh를 찾을 수 없습니다. HTTP만 사용합니다."
    # Fallback: 기존 HTTP 방식
    DURI_CORE_URL="http://localhost:8080"
    DURI_BRAIN_URL="http://localhost:8081"
    DURI_EVOLUTION_URL="http://localhost:8082"
    DURI_CONTROL_URL="http://localhost:8083"
}

# Tier 설정 로드 (우선순위: 환경변수 > Tier 파일 > 기본값)
if [ -f "var/run/shadow_tier.env" ]; then
    source "var/run/shadow_tier.env" 2>/dev/null || true
fi

# 전송 방식 설정 (기본값: HTTP, 환경변수로 오버라이드)
# DURI_SHADOW_TRANSPORT 또는 TRANSPORT 사용 (기존 코드 호환성)
# Tier 설정이 있으면 Tier 설정 우선
: "${TRANSPORT:=${SHADOW_TRANSPORT:-http}}"
: "${DURI_SHADOW_TRANSPORT:=${TRANSPORT}}"
: "${TRANSPORT:=$DURI_SHADOW_TRANSPORT}"  # http | ssh | mixed

# 카나리 설정 (mixed 모드용)
# 환경 변수 파일에서 동적 값 읽기 (카나리 제어기 지원)
if [ -f "var/run/canary.env" ]; then
    source "var/run/canary.env" 2>/dev/null || true
fi
# Tier 설정이 있으면 Tier 설정 우선
: "${SSH_CANARY:=${SHADOW_SSH_CANARY:-0.15}}"  # 15% 확률로 SSH 사용 (초기값, 카나리 제어기로 자동 조절)
: "${SSH_TIMEOUT:=8}"    # SSH 타임아웃 (초)
: "${SSH_RETRY:=2}"      # SSH 재시도 횟수
: "${CHAOS_ENABLED:=${SHADOW_CHAOS_ENABLED:-0}}"  # Tier-0,1에서는 기본 비활성화

# SSH 타겟 설정 (Docker 컨테이너 SSH 포트)
: "${SSH_CORE:=root@localhost:2220}"
: "${SSH_BRAIN:=root@localhost:2221}"
: "${SSH_EVOLUTION:=root@localhost:2222}"
: "${SSH_CONTROL:=root@localhost:2223}"

# 전송 어댑터에 SSH 설정 전달
export CORE_SSH="${SSH_CORE}"
export BRAIN_SSH="${SSH_BRAIN}"
export EVOLUTION_SSH="${SSH_EVOLUTION}"
export CONTROL_SSH="${SSH_CONTROL}"
export SSH_CANARY SSH_TIMEOUT SSH_RETRY

# API 엔드포인트 상수
LOOP_STATUS_ENDPOINT="/loop/status"
EMOTION_ENDPOINT="/api/emotion"
HEALTH_ENDPOINT="/health"

# 1. 단일 인스턴스 보장 (flock 락)
mkdir -p var/run
LOCK_FILE=var/run/shadow.lock
PID_FILE=var/run/shadow.pid

# ===== SAFEGUARD: never run from CI or non-interactive unless explicitly allowed =====
if [[ -n "${CI:-}" || -n "${GITHUB_ACTIONS:-}" ]]; then
  echo "[SAFEGUARD] CI 환경에서 shadow 스크립트 실행 차단"; exit 0
fi
if [[ ! -t 0 && "${ALLOW_SHADOW_NONINTERACTIVE:-0}" != "1" ]]; then
  echo "[SAFEGUARD] 비대화형 실행 차단 (ALLOW_SHADOW_NONINTERACTIVE=1 로 해제 가능)"; exit 0
fi
APPROVAL_FLAG=".shadow/ALLOW_RUN"
if [[ ! -f "$APPROVAL_FLAG" ]]; then
  echo "[SAFEGUARD] 승인 플래그($APPROVAL_FLAG) 없음 → 실행 차단"; exit 0
fi
# ===== /SAFEGUARD ================================================================


exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "[$(date)] Shadow 훈련장이 이미 실행 중입니다 (PID: $(cat "$PID_FILE" 2>/dev/null || echo 'unknown'))"
    exit 0
fi

# PID 저장
echo $$ > "$PID_FILE"
trap 'rm -f "$PID_FILE" "$LOCK_FILE"' EXIT

# 2. 로그 롤링 (최대 5개, 10MB)
mkdir -p var/logs
LOG_FILE=var/logs/shadow.log

if [ -f "$LOG_FILE" ]; then
    FILE_SIZE=$(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
    MAX_SIZE=$((10 * 1024 * 1024))  # 10MB

    if [ "$FILE_SIZE" -gt "$MAX_SIZE" ]; then
        echo "[$(date)] 로그 파일이 $MAX_SIZE 바이트를 초과했습니다. 롤링합니다..."
        for i in 5 4 3 2 1; do
            if [ -f "$LOG_FILE.$i" ]; then
                mv "$LOG_FILE.$i" "$LOG_FILE.$((i+1))"
            fi
        done
        mv "$LOG_FILE" "$LOG_FILE.1"
        touch "$LOG_FILE"
    fi
fi

# 로그 출력 리다이렉션
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "== 🎯 DuRi AI 연동 Shadow 훈련장 (최종 버전) =="
echo "시작 시간: $(date)"
echo "PID: $$"

# 서브모듈 동기화 (SSH 연결된 서브모듈들)
echo "🔄 서브모듈 동기화 시작..."
source scripts/lib/submodule_sync.sh
sync_all_submodules

# DuRi AI 서비스 상태 확인 (하이브리드 전송 사용, 윈도우 합격: 연속 2/3 성공, 총 대기 45s)
check_duri_services() {
    echo "[$(date)] DuRi AI 서비스 상태 확인 (TRANSPORT=$TRANSPORT, 윈도우 합격: 2/3 성공)..."
    
    local services=("core" "brain" "evolution" "control")
    local all_ok=0  # 초기값: 0 (모든 서비스 OK 가정)
    local max_wait=45  # 총 대기 시간 (초)
    local window_size=3  # 윈도우 크기
    local pass_threshold=2  # 합격 임계값 (연속 2/3 성공)
    
    for service in "${services[@]}"; do
        local start_time=$(date +%s)
        local success_count=0
        local attempt=0
        local service_ok=0
        
        while [ $(( $(date +%s) - start_time )) -lt $max_wait ]; do
            attempt=$((attempt + 1))
            if call_service "$service" "$HEALTH_ENDPOINT" "GET" "" >/dev/null 2>&1; then
                success_count=$((success_count + 1))
                if [ $success_count -ge $pass_threshold ]; then
                    echo "✅ $service: OK (윈도우 합격: $success_count/$attempt)"
                    service_ok=1
                    break
                fi
            else
                success_count=0  # 연속 실패 시 리셋
            fi
            sleep 1
        done
        
        if [ $service_ok -eq 0 ]; then
            echo "❌ $service: FAIL (윈도우 합격 실패: $success_count/$attempt)"
            all_ok=1  # 하나라도 실패하면 1로 변경
        fi
    done
    
    # 반환값: 0=성공, 1=실패
    # all_ok: 0=모든 서비스 OK, 1=일부 실패
    if [ $all_ok -eq 0 ]; then
        return 0  # 모든 서비스 OK
    else
        return 1  # 일부 서비스 실패
    fi
}

# 감정 기반 훈련 (하이브리드 전송 사용)
train_with_emotion() {
    local emotions=("happy" "sad" "angry" "fear" "surprise" "disgust")
    local emotion="${emotions[$((RANDOM % ${#emotions[@]}))]}"
    local timestamp=$(date -Iseconds)

    echo "[$(date)] 감정 기반 훈련 시작 (감정: $emotion, TRANSPORT=$TRANSPORT)..."

    # JSON 데이터 생성 (jq 사용, 기존 패턴)
    local payload
    if command -v jq >/dev/null 2>&1; then
        payload=$(jq -n \
            --arg emotion "$emotion" \
            --arg timestamp "$timestamp" \
            --arg request_id "shadow-$emotion-$(date +%s)" \
            --argjson intensity 0.5 \
            '{
                emotion: $emotion,
                timestamp: $timestamp,
                data: {
                    text: "shadow training ping",
                    source: "shadow_v2",
                    meta: {
                        request_id: $request_id
                    }
                },
                intensity: $intensity
            }')
    else
        # jq 없을 때 fallback
        payload="{\"emotion\":\"$emotion\",\"timestamp\":\"$timestamp\",\"data\":{\"text\":\"shadow training ping\",\"source\":\"shadow_v2\",\"meta\":{\"request_id\":\"shadow-$emotion-$(date +%s)\"}},\"intensity\":0.5}"
    fi

    # duri-core에 감정 데이터 전송 (하이브리드 전송, 재시도/타임아웃/원인코드 로깅)
    local response
    local retry_count=0
    local max_retries=3
    local backoff=0.7
    local per_try_timeout=3  # 서버가 즉시 202 응답하므로 3s로 낮춤 (내부 타임아웃 2s + 여유)
    local last_error=""
    
    while [ $retry_count -le $max_retries ]; do
        if [ "$TRANSPORT" = "ssh" ] && [ -z "${CORE_SSH:-}" ]; then
            echo "[$(date)] [WARN] TRANSPORT=ssh인데 CORE_SSH 미설정, HTTP 폴백 시도..." >&2
            export TRANSPORT=http
        fi
        
        if response=$(timeout $per_try_timeout scripts/cli/send_emotion "$emotion" 2>&1); then
            local exit_code=${PIPESTATUS[0]}
            if [ $exit_code -eq 0 ]; then
                echo "[$(date)] 감정 응답: $response"
                return 0
            else
                last_error="exit_code=$exit_code"
            fi
        else
            local exit_code=${PIPESTATUS[0]}
            if [ $exit_code -eq 124 ]; then
                last_error="timeout (${per_try_timeout}s)"
            elif [ $exit_code -eq 7 ]; then
                last_error="connection_failed"
            elif [ $exit_code -eq 22 ]; then
                last_error="http_404_or_401"
            else
                last_error="exit_code=$exit_code"
            fi
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -le $max_retries ]; then
            echo "[$(date)] 감정 전송 재시도 ($retry_count/$max_retries, 원인: $last_error, backoff: ${backoff}s)..." >&2
            sleep $backoff
        fi
    done
    
    # SSH 실패 시 HTTP 폴백 1회 (SSH 모드일 때만)
    if [ "$TRANSPORT" = "ssh" ] && [ $retry_count -gt $max_retries ]; then
        echo "[$(date)] [FALLBACK] SSH 실패, HTTP 폴백 1회 시도..." >&2
        local orig_transport="$TRANSPORT"
        export TRANSPORT=http
        if response=$(timeout $per_try_timeout scripts/cli/send_emotion "$emotion" 2>&1); then
            echo "[$(date)] 감정 응답 (HTTP 폴백): $response"
            export TRANSPORT="$orig_transport"
            return 0
        else
            export TRANSPORT="$orig_transport"
        fi
    fi
    
    echo "[$(date)] 감정 전송 실패 (TRANSPORT=$TRANSPORT, 원인: $last_error, 재시도 초과)" >&2
    return 1
}

# 루프 상태 조회 훈련 (하이브리드 전송 사용)
train_with_loop_status() {
    local session_id="shadow-session-$(date +%s)"

    echo "[$(date)] 루프 상태 조회 훈련 시작 (TRANSPORT=$TRANSPORT)..."

    # duri-core에 루프 상태 조회 요청 (하이브리드 전송)
    local path="${LOOP_STATUS_ENDPOINT}/${session_id}"
    local response
    if response=$(call_core "$path" "GET" "" 2>&1); then
        echo "[$(date)] 루프 상태 응답: $response"
    else
        echo "[$(date)] 루프 상태 조회 실패 (TRANSPORT=$TRANSPORT)"
        return 1
    fi
}

# 진화 증거 수집 함수 (하드닝 #2: 단일 함수로 고정, 에러 시 재시도 1회, Δ2: 비동기화)
_collect_evolution_evidence() {
    local ev_id="${EV_ID:-EV-$(date -u +%Y%m%d-%H%M%S)-$(awk 'BEGIN{srand(); printf "%02d", int(rand()*100)}')}"
    echo "SHADOW_EV_BUNDLE_START ev=${ev_id} ts=$(date +%s)" >> var/logs/shadow.log
    echo "[$(date)] 진화 증거 수집 시작 (EV 번들 생성, ev=${ev_id})..."
    
        # Δ2: Bundle 비동기화 옵션 (환경변수로 제어)
        : "${BUNDLE_ASYNC:=0}"
        
        local retry_count=0
        local max_retries=1
        
        while [ $retry_count -le $max_retries ]; do
            if [ -f "scripts/evolution/evidence_bundle.sh" ]; then
                # Shadow 훈련 메트릭을 EV 번들에 포함하기 위해 TRANSPORT 환경 변수 전달
                # Δ2: 비동기 실행 옵션
                if [ "${BUNDLE_ASYNC}" = "1" ]; then
                    TRANSPORT="${TRANSPORT:-http}" ASYNC=1 BUNDLE_TIMEOUT=90 bash scripts/evolution/evidence_bundle.sh 2>&1 | tee -a "$LOG_FILE" &
                    echo "[INFO] Bundle 비동기 실행 중 (백그라운드)"
                else
                    # (6) 타임아웃 90s 유지 + 번들 동시성 힌트: 실패 시 재시도 1회
                    if TRANSPORT="${TRANSPORT:-http}" timeout 90s bash scripts/evolution/evidence_bundle.sh 2>&1 | tee -a "$LOG_FILE"; then
                        # EV 점수 계산 (p-value 등 분석)
                        if [ -f "scripts/evolution/evidence_score.sh" ]; then
                            bash scripts/evolution/evidence_score.sh 2>&1 | tee -a "$LOG_FILE" || echo "⚠️ EV 점수 계산 스킵"
                        fi
                
                # 자가 진화 분석 결과를 최신 EV 번들에 통합
                local latest_ev
                latest_ev=$(readlink -f var/evolution/LATEST 2>/dev/null || find var/evolution -maxdepth 1 -type d -name 'EV-*' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | awk '{print $2}')
                if [ -n "$latest_ev" ] && [ -d "$latest_ev" ]; then
                    echo "[$(date)] 자가 진화 분석 결과를 EV 번들에 통합: $latest_ev"
                    
                    # 자가 진화 분석 결과 파일이 있으면 EV 번들에 복사
                    if ls var/reports/evolution_*.md >/dev/null 2>&1; then
                        cp var/reports/evolution_*.md "$latest_ev/" 2>/dev/null || true
                    fi
                    
                    # Shadow 훈련 메트릭을 EV 번들 summary.txt에 추가
                    if [ -f "$latest_ev/summary.txt" ]; then
                        {
                            echo "# Shadow 훈련 메트릭 ($(date -Iseconds))"
                            echo "shadow_training_completed=$(date -Iseconds)"
                            echo "transport_mode=${TRANSPORT}"
                            [ -f var/logs/shadow.log ] && echo "shadow_log_size=$(wc -l < var/logs/shadow.log 2>/dev/null || echo 0)"
                        } >> "$latest_ev/summary.txt" 2>/dev/null || true
                    fi
                fi
                
                        echo "[$(date)] 진화 증거 수집 완료"
                        echo "SHADOW_EV_BUNDLE_END ev=${ev_id} ts=$(date +%s) status=ok" >> var/logs/shadow.log
                        return 0
                    else
                        # (6) 타임아웃 실패 시 재시도 1회
                        echo "[WARN] bundle timeout → retry once" >&2
                        if TRANSPORT="${TRANSPORT:-http}" timeout 90s bash scripts/evolution/evidence_bundle.sh 2>&1 | tee -a "$LOG_FILE"; then
                            echo "[OK] bundle 재시도 성공"
                            if [ -f "scripts/evolution/evidence_score.sh" ]; then
                                bash scripts/evolution/evidence_score.sh 2>&1 | tee -a "$LOG_FILE" || echo "⚠️ EV 점수 계산 스킵"
                            fi
                            echo "[$(date)] 진화 증거 수집 완료 (재시도)"
                            echo "SHADOW_EV_BUNDLE_END ev=${ev_id} ts=$(date +%s) status=ok" >> var/logs/shadow.log
                            return 0
                        else
                            echo "[FAIL] bundle twice timeout" >&2
                            retry_count=$((retry_count + 1))
                            if [ $retry_count -le $max_retries ]; then
                                echo "[$(date)] EV 번들 생성 실패, 재시도 ($retry_count/$max_retries)..."
                                sleep 2
                            fi
                        fi
                    fi
        else
            echo "⚠️ evidence_bundle.sh 없음 - 진화 증거 수집 스킵"
            return 1
        fi
    done
    
    # 런당 최소 1 EV 보장 (실패 시에도 빈껍데기라도 기록)
    echo "[$(date)] 진화 증거 수집 실패 → 빈껍데기 EV 생성 (런당 최소 1 EV 보장)..."
    local ev_dir="var/evolution/EV-$(date -u +%Y%m%d-%H%M%S)-99"
    mkdir -p "$ev_dir"
    {
        echo "# Shadow 훈련 메트릭 (실패 복구)"
        echo "shadow_training_completed=$(date -Iseconds)"
        echo "transport_mode=${TRANSPORT:-http}"
        echo "ev_creation_status=FAILED_RECOVERY"
        echo "ev_recovery_timestamp=$(date -Iseconds)"
    } > "$ev_dir/summary.txt" 2>/dev/null || true
    ln -sfn "$(realpath --relative-to=var/evolution "$ev_dir")" var/evolution/LATEST 2>/dev/null || true
    echo "[$(date)] 빈껍데기 EV 생성 완료: $ev_dir"
    return 0
}

# 메인 훈련 루프
main_training_loop() {
    EV_ID="EV-$(date -u +%Y%m%d-%H%M%S)-$(awk 'BEGIN{srand(); printf "%02d", int(rand()*100)}')"
    
    # (1) Epoch END/Duration "확실히" 찍히게 보강: 함수형 finally 덧씌우기
    {
        START_TS=$(date +%s)
        EV_ID="${EV_ID:-UNK}"
        _epoch_finalized=0
        
        _finalize_epoch() {
            [[ "${_epoch_finalized:-0}" -eq 1 ]] && return 0
            _epoch_finalized=1
            END_TS=$(date +%s)
            DUR=$((END_TS - START_TS))
            echo "SHADOW_EPOCH_END ev=${EV_ID} ts=${END_TS} dur=${DUR}" >> var/logs/shadow.log
            echo "SHADOW_EPOCH_DURATION ev=${EV_ID} duration=${DUR}s" >> var/logs/shadow.log
            
            # Prometheus textfile 노출
            local textfile_dir="${TEXTFILE_DIR:-/var/lib/node_exporter/textfile_collector}"
            mkdir -p "$textfile_dir" 2>/dev/null || true
            if [ -d "$textfile_dir" ]; then
                printf 'duri_shadow_epoch_duration_seconds{ev="%s"} %d\n' "${EV_ID}" "${DUR}" \
                    > "${textfile_dir}/duri_shadow_epoch.prom.$$"
                mv "${textfile_dir}/duri_shadow_epoch.prom.$$" \
                   "${textfile_dir}/duri_shadow_epoch.prom" 2>/dev/null || true
            fi
        }
        
        trap '_finalize_epoch; rm -f "$PID_FILE" "$LOCK_FILE" 2>/dev/null || true' EXIT INT TERM
    } 2>/dev/null
    
    echo "SHADOW_EPOCH_START ev=${EV_ID} ts=${START_TS}" >> var/logs/shadow.log
    echo "[$(date)] DuRi AI 연동 Shadow 훈련 시작... (EV=${EV_ID})"

    # 1. 서비스 상태 확인
    if ! check_duri_services; then
        echo "[$(date)] DuRi AI 서비스가 준비되지 않았습니다. (ALLOW_READYFAIL=1 이면 강행)"
        if [ "${ALLOW_READYFAIL:-0}" = "1" ]; then
            echo "[OVERRIDE] readiness gate bypass (pilot)"
        else
            return 1
        fi
    fi

    # 2. 감정 기반 훈련
    train_with_emotion

    # 3. 루프 상태 조회 훈련
    train_with_loop_status

    echo "[$(date)] 기본 훈련 완료"

    # 4. 약점 분석 (Weakpoint Analysis)
    echo "[$(date)] 약점 분석 시작..."
    if [ -f "scripts/weakpoint_topk.py" ]; then
        # weakpoint_topk.py는 인자 없이 실행 (기본 동작)
        python scripts/weakpoint_topk.py 2>/dev/null || echo "⚠️ 약점 분석 스킵"
    else
        echo "⚠️ weakpoint_topk.py 없음 - 스킵"
    fi

    # 5. 자가 진화 분석 (Self-Evolution Analysis)
    echo "[$(date)] 자가 진화 분석 시작..."
    if [ -f "duri_modules/self_awareness/integrated_self_evolution_system.py" ]; then
        python -m duri_modules.self_awareness.integrated_self_evolution_system \
            --input var/logs/shadow.log \
            --prom http://localhost:9090 \
            --out var/reports/evolution_$(date +%Y%m%d_%H%M%S).md 2>/dev/null || echo "⚠️ 자가 진화 분석 스킵"
    else
        echo "⚠️ integrated_self_evolution_system.py 없음 - 스킵"
    fi

    # 6. 코딩 시뮬레이션 (품질 게이트 드라이런)
    echo "[$(date)] 품질 게이트 드라이런 시작..."
    if [ -f "scripts/shadow_parallel_validator.sh" ]; then
        bash scripts/shadow_parallel_validator.sh \
            --paths duri_core duri_brain duri_evolution duri_control \
            --report var/reports/quality_gate_$(date +%Y%m%d_%H%M%S).md 2>/dev/null || echo "⚠️ 품질 게이트 드라이런 스킵"
    else
        echo "⚠️ shadow_parallel_validator.sh 없음 - 스킵"
    fi

    # 7. 프로모션 준비 (스냅샷 태그)
    echo "[$(date)] 프로모션 준비 (스냅샷 태그 생성)..."
    for module in duri_core duri_brain duri_evolution duri_control; do
        if [ -d "$HOME/DuRiShadow/$module" ]; then
            TAG="shadow-$(date +%Y%m%d-%H%M%S)-$module"
            git -C "$HOME/DuRiShadow/$module" tag -f "$TAG" 2>/dev/null && \
            echo "✅ $module: $TAG" || echo "⚠️ $module: 태그 생성 실패"
        fi
    done

    echo "[$(date)] DuRi AI 연동 Shadow 훈련 완료"
    # Γ5: trap EXIT에서 END/Duration 기록 (비정상 종료 포함)
    END_TS=$(date +%s)
    DUR=$((END_TS - START_TS))
    echo "SHADOW_EPOCH_END ev=${EV_ID:-N/A} ts=${END_TS} dur=${DUR} status=ok" >> var/logs/shadow.log
    echo "SHADOW_EPOCH_DURATION ev=${EV_ID} duration=${DUR}s" >> var/logs/shadow.log
    echo "[INFO] Shadow Epoch 소요시간: ${DUR}s (목표: 600-900s)"
    
    # Prometheus textfile 노출 (node_exporter textfile_collector)
    TEXTFILE_DIR="${TEXTFILE_DIR:-/var/lib/node_exporter/textfile_collector}"
    mkdir -p "$TEXTFILE_DIR" 2>/dev/null || true
    if [ -d "$TEXTFILE_DIR" ]; then
        printf 'duri_shadow_epoch_duration_seconds{ev="%s"} %d\n' "${EV_ID}" "${DUR}" \
            > "${TEXTFILE_DIR}/duri_shadow_epoch.prom.$$"
        mv "${TEXTFILE_DIR}/duri_shadow_epoch.prom.$$" \
           "${TEXTFILE_DIR}/duri_shadow_epoch.prom" 2>/dev/null || true
    fi
    
    # trap 해제 (정상 종료 시)
    trap - EXIT

    # 진화 증거 수집: EV 번들 생성 및 점수 계산 (하드닝 #2: 단일 함수로 고정)
    _collect_evolution_evidence
}

# 무한 루프 실행
while true; do
    main_training_loop

    echo "[$(date)] 2시간 대기 중..."
    sleep 7200  # 2시간
done
