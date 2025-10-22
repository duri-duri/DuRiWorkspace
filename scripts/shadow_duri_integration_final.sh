#!/usr/bin/env bash
set -e
cd /home/duri/DuRiWorkspace

echo "== 🎯 DuRi AI 연동 Shadow 훈련장 (최종 버전) =="
echo "시작 시간: $(date)"

# 서브모듈 동기화 (SSH 연결된 서브모듈들)
echo "🔄 서브모듈 동기화 시작..."
source scripts/lib/submodule_sync.sh
sync_all_submodules

# DuRi AI 서비스 상태 확인
check_duri_services() {
    echo "[$(date)] DuRi AI 서비스 상태 확인..."
    for port in 8080 8081 8082 8083; do
        if curl -sf "http://localhost:$port/health" >/dev/null; then
            echo "✅ duri-$port: OK"
        else
            echo "❌ duri-$port: FAIL"
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
    local response=$(curl -X POST "http://localhost:8080/api/emotion" \
        -H "Content-Type: application/json" \
        -d "{\"emotion\": \"$emotion\", \"timestamp\": \"$timestamp\", \"data\": {\"text\": \"shadow training ping\", \"source\": \"shadow_v2\", \"meta\": {\"request_id\": \"shadow-$emotion-$(date +%s)\"}}, \"intensity\": 0.5}" \
        -s)

    echo "[$(date)] 감정 응답: $response"
}

# 루프 상태 조회 훈련
train_with_loop_status() {
    local session_id="shadow-session-$(date +%s)"

    echo "[$(date)] 루프 상태 조회 훈련 시작..."

    # duri-core에 루프 상태 조회 요청
    local response=$(curl -s "http://localhost:8080/api/loop/status/$session_id")

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

    echo "[$(date)] DuRi AI 연동 Shadow 훈련 완료"
}

# 무한 루프 실행
while true; do
    main_training_loop

    echo "[$(date)] 2시간 대기 중..."
    sleep 7200  # 2시간
done
