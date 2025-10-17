#!/usr/bin/env bash
set -euo pipefail

# Shadow 훈련장 낮 시간대 운영 스크립트
# 원장님이 직접 작업하는 시간에만 shadow 훈련장을 켜두는 방식

echo "=== 🌅 Shadow 훈련장 낮 시간대 운영 ==="
echo "실행 시간: $(date)"
echo ""

case "${1:-start}" in
    "start")
        echo "🚀 Shadow 훈련장 시작"
        
        # 1. Shadow 훈련 서비스 시작
        echo "   - duri_core, duri_brain, duri_evolution 시작 중..."
        docker compose up -d duri_core duri_brain duri_evolution
        
        # 2. Shadow 활성화
        echo "   - Shadow 활성화 중..."
        docker compose exec duri-redis redis-cli SET shadow:enabled 1
        
        # 3. 카나리 비율 설정 (10%부터 시작)
        echo "   - 카나리 비율 10% 설정..."
        docker compose exec duri-redis redis-cli SET canary:ratio 0.1
        
        # 4. 상태 확인
        echo "   - 서비스 상태 확인..."
        docker compose ps | grep -E "(duri_core|duri_brain|duri_evolution)"
        
        echo ""
        echo "✅ Shadow 훈련장 시작 완료"
        echo "🎯 다음 단계:"
        echo "   - 10분 후: ./check_srm_and_guard.sh"
        echo "   - 30분 후: ./run_promote_canary.sh 0.50"
        echo "   - 저녁 퇴근 시: ./ops/shadow_workday.sh stop"
        ;;
        
    "stop")
        echo "🌙 Shadow 훈련장 중지"
        
        # 1. 카나리 비율 0으로 설정
        echo "   - 카나리 비율 0으로 설정..."
        docker compose exec duri-redis redis-cli SET canary:ratio 0
        
        # 2. Shadow 비활성화
        echo "   - Shadow 비활성화..."
        docker compose exec duri-redis redis-cli SET shadow:enabled 0
        
        # 3. Shadow 훈련 서비스 중지
        echo "   - duri_core, duri_brain, duri_evolution 중지 중..."
        docker compose stop duri_core duri_brain duri_evolution
        
        # 4. 상태 확인
        echo "   - 서비스 상태 확인..."
        docker compose ps | grep -E "(duri_core|duri_brain|duri_evolution)"
        
        echo ""
        echo "✅ Shadow 훈련장 중지 완료"
        echo "🎯 다음 단계:"
        echo "   - 내일 아침: ./ops/shadow_workday.sh start"
        echo "   - duri_head는 계속 실행 중 (DB/Redis/control/monitoring)"
        ;;
        
    "status")
        echo "📊 Shadow 훈련장 상태 확인"
        
        echo "   - 서비스 상태:"
        docker compose ps | grep -E "(duri_core|duri_brain|duri_evolution|duri_control|duri-postgres|duri-redis)"
        
        echo "   - Redis 설정:"
        echo "     shadow:enabled = $(docker compose exec duri-redis redis-cli GET shadow:enabled 2>/dev/null || echo 'N/A')"
        echo "     canary:ratio = $(docker compose exec duri-redis redis-cli GET canary:ratio 2>/dev/null || echo 'N/A')"
        
        echo "   - 최근 승격 결정:"
        docker compose exec duri-postgres psql -U duri -d duri -c \
        "SELECT model_id, decision, reason, decision_ts FROM v_promotion_latest ORDER BY decision_ts DESC LIMIT 3;" 2>/dev/null || echo "     DB 연결 실패"
        ;;
        
    *)
        echo "사용법: $0 {start|stop|status}"
        echo ""
        echo "  start  - Shadow 훈련장 시작 (낮 시간대)"
        echo "  stop   - Shadow 훈련장 중지 (저녁 퇴근 시)"
        echo "  status - 현재 상태 확인"
        echo ""
        echo "예시:"
        echo "  $0 start   # 아침에 실행"
        echo "  $0 stop    # 저녁에 실행"
        echo "  $0 status  # 언제든 상태 확인"
        exit 1
        ;;
esac

echo ""
echo "⏰ 실행 시간: $(date)"
