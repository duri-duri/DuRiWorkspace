#!/usr/bin/env bash
set -e
cd /home/duri/DuRiWorkspace

echo "== 🎯 DuRi AI 연동 Shadow 훈련장 =="
echo "시작 시간: $(date)"

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

# 감정 벡터 기반 훈련
train_with_emotion_vector() {
    local emotion_vector="[0.1, 0.2, 0.3, 0.4, 0.5]"
    local timestamp=$(date -Iseconds)

    echo "[$(date)] 감정 벡터 훈련 시작..."

    # duri-core에 감정 벡터 전송
    local response=$(curl -X POST "http://localhost:8080/emotion/vector" \
        -H "Content-Type: application/json" \
        -d "{\"emotion_vector\": $emotion_vector, \"timestamp\": \"$timestamp\"}" \
        -s)

    echo "[$(date)] 감정 벡터 응답: $response"
}

# 루프 처리 훈련
train_with_loop_process() {
    local emotion="joy"
    local timestamp=$(date -Iseconds)

    echo "[$(date)] 루프 처리 훈련 시작..."

    # duri-core에 루프 처리 요청
    local response=$(curl -X POST "http://localhost:8080/loop/process" \
        -H "Content-Type: application/json" \
        -d "{\"emotion\": \"$emotion\", \"data\": {\"test\": \"shadow_training\", \"timestamp\": \"$timestamp\"}, \"timestamp\": \"$timestamp\"}" \
        -s)

    echo "[$(date)] 루프 처리 응답: $response"
}

# 학습된 패턴 분석
analyze_patterns() {
    echo "[$(date)] 학습된 패턴 분석..."

    local patterns=$(curl -s "http://localhost:8080/patterns")
    echo "[$(date)] 패턴 데이터: $patterns"
}

# 메인 훈련 루프
main_training_loop() {
    echo "[$(date)] DuRi AI 연동 Shadow 훈련 시작..."

    # 1. 서비스 상태 확인
    if ! check_duri_services; then
        echo "[$(date)] DuRi AI 서비스가 준비되지 않았습니다."
        return 1
    fi

    # 2. 감정 벡터 훈련
    train_with_emotion_vector

    # 3. 루프 처리 훈련
    train_with_loop_process

    # 4. 패턴 분석
    analyze_patterns

    echo "[$(date)] DuRi AI 연동 Shadow 훈련 완료"
}

# 무한 루프 실행
while true; do
    main_training_loop

    echo "[$(date)] 2시간 대기 중..."
    sleep 7200  # 2시간
done
