#!/usr/bin/env bash
set -e
cd /home/duri/DuRiWorkspace

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

# 서비스 엔드포인트 상수 정의 (config/common_app.json 기준)
DURI_CORE_URL="http://localhost:8080"
DURI_BRAIN_URL="http://localhost:8081"
DURI_EVOLUTION_URL="http://localhost:8082"
DURI_CONTROL_URL="http://localhost:8083"

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

# DuRi AI 서비스 상태 확인
check_duri_services() {
    echo "[$(date)] DuRi AI 서비스 상태 확인..."
    for url in "$DURI_CORE_URL" "$DURI_BRAIN_URL" "$DURI_EVOLUTION_URL" "$DURI_CONTROL_URL"; do
        if curl -sf "$url$HEALTH_ENDPOINT" >/dev/null; then
            echo "✅ $url: OK"
        else
            echo "❌ $url: FAIL"
            return 1
        fi
    done
    return 0
}

# 감정 기반 훈련 (허용되는 감정값 사용)
train_with_emotion() {
    local emotions=("happy" "sad" "angry" "fear" "surprise" "disgust")
    local emotion="${emotions[$((RANDOM % ${#emotions[@]}))]}"
    local timestamp=$(date -Iseconds)

    echo "[$(date)] 감정 기반 훈련 시작 (감정: $emotion)..."

    # duri-core에 감정 데이터 전송 (허용되는 감정값 사용)
    local response=$(curl -X POST "$DURI_CORE_URL$EMOTION_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{\"emotion\": \"$emotion\", \"timestamp\": \"$timestamp\", \"data\": {\"text\": \"shadow training ping\", \"source\": \"shadow_v2\", \"meta\": {\"request_id\": \"shadow-$emotion-$(date +%s)\"}}, \"intensity\": 0.5}" \
        -s)

    echo "[$(date)] 감정 응답: $response"
}

# 루프 상태 조회 훈련
train_with_loop_status() {
    local session_id="shadow-session-$(date +%s)"

    echo "[$(date)] 루프 상태 조회 훈련 시작..."

    # duri-core에 루프 상태 조회 요청 (표준 경로: /loop/status/<session_id>)
    local response=$(curl -s "$DURI_CORE_URL$LOOP_STATUS_ENDPOINT/$session_id")

    echo "[$(date)] 루프 상태 응답: $response"
}

# 메인 훈련 루프
main_training_loop() {
    echo "[$(date)] DuRi AI 연동 Shadow 훈련 시작..."

    # 1. 서비스 상태 확인
    if ! check_duri_services; then
        echo "[$(date)] DuRi AI 서비스가 준비되지 않았습니다."
        return 1
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
}

# 무한 루프 실행
while true; do
    main_training_loop

    echo "[$(date)] 2시간 대기 중..."
    sleep 7200  # 2시간
done
