#!/usr/bin/env bash
set -euo pipefail
cd /home/duri/DuRiWorkspace

# 일일 게이트 리포트: 오늘 수치 + 7일 이동평균 + 자동 코멘트(원인/액션)
DAY=$(date +%F)
REPORT_DIR="var/reports"
mkdir -p "$REPORT_DIR"

echo "📊 일일 게이트 리포트 생성 중: $DAY"

# Redis에서 오늘 지표 가져오기
ACC=$(docker compose exec -T duri-redis redis-cli GET gate:accuracy:$DAY || echo "0")
P95=$(docker compose exec -T duri-redis redis-cli GET gate:latency_p95:$DAY || echo "0")
CPT=$(docker compose exec -T duri-redis redis-cli GET gate:cost_per_1k:$DAY || echo "0")
VIO=$(docker compose exec -T duri-redis redis-cli GET gate:violations:$DAY || echo "0")

# 7일 이동평균 계산
ACC_7D=$(docker compose exec -T duri-postgres psql -U duri -d duri -Atc "
  SELECT COALESCE(AVG(accuracy::float), 0) 
  FROM (
    SELECT accuracy::float 
    FROM (
      SELECT key, value as accuracy 
      FROM redis_keys 
      WHERE key LIKE 'gate:accuracy:%' 
      AND key >= 'gate:accuracy:$(date -d '7 days ago' +%F)'
      ORDER BY key DESC LIMIT 7
    ) t
  ) s;
" 2>/dev/null || echo "0")

P95_7D=$(docker compose exec -T duri-postgres psql -U duri -d duri -Atc "
  SELECT COALESCE(AVG(latency_p95::float), 0) 
  FROM (
    SELECT latency_p95::float 
    FROM (
      SELECT key, value as latency_p95 
      FROM redis_keys 
      WHERE key LIKE 'gate:latency_p95:%' 
      AND key >= 'gate:latency_p95:$(date -d '7 days ago' +%F)'
      ORDER BY key DESC LIMIT 7
    ) t
  ) s;
" 2>/dev/null || echo "0")

# 자동 코멘트 생성
COMMENTS=""
if (( $(echo "$P95 > $P95_7D * 1.5" | bc -l) )); then
  COMMENTS="$COMMENTS\n- ⚠️ **지연시간 증가**: p95=$P95 (7일 평균: $P95_7D) → DB 연결 수 +2, 쿼리 캐시 점검 제안"
fi

if (( $(echo "$ACC < $ACC_7D * 0.95" | bc -l) )); then
  COMMENTS="$COMMENTS\n- ⚠️ **정확도 하락**: accuracy=$ACC (7일 평균: $ACC_7D) → 평가셋 섞임 가능성, 최근 추가 태그 집중 점검"
fi

if (( $(echo "$VIO > 0" | bc -l) )); then
  COMMENTS="$COMMENTS\n- 🚨 **정책 위반**: $VIO건 → 안전 가드 강화 필요"
fi

if [ -z "$COMMENTS" ]; then
  COMMENTS="\n- ✅ **모든 지표 정상**: 안정적인 운영 중"
fi

# 마크다운 리포트 생성
cat > "$REPORT_DIR/gate_daily_$DAY.md" << EOF
# DuRi 게이트 일일 리포트 - $DAY

## 📊 오늘 지표
- **정확도**: $ACC (7일 평균: $ACC_7D)
- **지연시간 p95**: ${P95}ms (7일 평균: ${P95_7D}ms)
- **비용/1K**: \$$CPT (7일 평균: 계산 중)
- **정책 위반**: $VIO건

## 📈 추세 분석
$COMMENTS

## 🎯 권장 액션
- Coach 배치 성능 모니터링
- 툴 호출 최적화 검토
- 평가셋 품질 점검

## 📋 다음 실행 예정
- 내일 09:00: Shadow 훈련장 시작
- 내일 16:00: Shadow 훈련장 중지

---
*자동 생성: $(date '+%Y-%m-%d %H:%M:%S')*
EOF

echo "✅ 일일 리포트 생성 완료: $REPORT_DIR/gate_daily_$DAY.md"

# Redis에 리포트 요약 저장
docker compose exec -T duri-redis redis-cli SETEX "report:daily:$DAY" 86400 "$(cat "$REPORT_DIR/gate_daily_$DAY.md")"
