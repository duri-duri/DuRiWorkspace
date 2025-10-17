#!/bin/bash
# Trace v2 운영 체크 스크립트
# 하루 2회 자동 건강검진: 큐→적재 스모크 + 뷰 집계 확인

set -euo pipefail

echo "=== 🧪 Trace v2 운영 체크 ==="
echo "실행 시간: $(date)"
echo ""

# 1. 큐→적재 스모크 테스트
echo "**1. 큐→적재 스모크 테스트:**"
SMOKE_UUID=$(python3 -c "import uuid; print(uuid.uuid4())")
echo "Smoke UUID: $SMOKE_UUID"

# Redis 큐에 테스트 이벤트 삽입
docker compose -p duriworkspace exec duri-redis redis-cli RPUSH trace:events "{\"kind\":\"span_upsert\",\"span\":{\"span_id\":\"$SMOKE_UUID\",\"parent_span_id\":null,\"deploy_req_id\":\"ops-check-$(date +%s)\",\"artifact_id\":null,\"span_name\":\"ops_check_smoke\",\"status\":\"ok\",\"start_ts\":\"$(date -u +%FT%TZ)\",\"end_ts\":null,\"labels\":{\"source\":\"ops\",\"env\":\"staging\",\"service\":\"ops_check\"},\"attrs\":{\"note\":\"ops_check_smoke\"}}}"

echo "✅ 테스트 이벤트 큐에 삽입 완료"

# 2. ETL 처리 대기 및 확인
echo "**2. ETL 처리 대기 (5초):**"
sleep 5

# 3. DB에서 테스트 이벤트 확인
echo "**3. DB에서 테스트 이벤트 확인:**"
RESULT=$(docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -t -c "SELECT count(*) FROM trace_span WHERE span_id = '$SMOKE_UUID';" | tr -d ' ')

if [ "$RESULT" = "1" ]; then
    echo "✅ 스모크 테스트 성공: 테스트 이벤트가 DB에 정상 적재됨"
else
    echo "❌ 스모크 테스트 실패: 테스트 이벤트가 DB에 없음 (count: $RESULT)"
    exit 1
fi

# 4. 뷰 집계 확인
echo "**4. 뷰 집계 확인:**"
docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -c "
SELECT 
  'v_trace_performance_summary' as view_name,
  total_records,
  last_hour,
  last_day,
  error_rate
FROM v_trace_performance_summary
WHERE table_name = 'trace_span';
"

# 5. 데이터 품질 체크
echo "**5. 데이터 품질 체크:**"
docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -c "
SELECT * FROM check_trace_data_quality();
"

# 6. Redis 큐 상태 확인
echo "**6. Redis 큐 상태 확인:**"
QUEUE_LENGTH=$(docker compose -p duriworkspace exec duri-redis redis-cli LLEN trace:events)
DLQ_LENGTH=$(docker compose -p duriworkspace exec duri-redis redis-cli LLEN trace:dead)

echo "   - trace:events 큐 길이: $QUEUE_LENGTH"
echo "   - trace:dead DLQ 길이: $DLQ_LENGTH"

if [ "$QUEUE_LENGTH" -gt 100 ]; then
    echo "⚠️  큐 길이가 높음: $QUEUE_LENGTH"
fi

if [ "$DLQ_LENGTH" -gt 0 ]; then
    echo "⚠️  DLQ에 실패 이벤트 있음: $DLQ_LENGTH"
fi

# 7. 테스트 데이터 정리
echo "**7. 테스트 데이터 정리:**"
docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -c "DELETE FROM trace_span WHERE span_id = '$SMOKE_UUID';"
echo "✅ 테스트 데이터 정리 완료"

echo ""
echo "✅ Trace v2 운영 체크 완료!"