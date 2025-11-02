#!/usr/bin/env bash
# DuRi Doctor: 단일 진단 엔트리 - 정량 지표→원인 추정→수정 가이드
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== DuRi Doctor ==="
echo ""

# 1) Cadence (EV 생성 속도)
echo "## 1. EV 생성 속도"
EV_VEL=$(bash scripts/ev_velocity.sh 2>/dev/null | awk '{print $2}' || echo "0")
echo "EV_velocity(h): $EV_VEL"
if (( $(echo "$EV_VEL < 2.5" | bc -l 2>/dev/null || echo "1") )); then
  echo "[CAUSE] 생성 주기/워커 병렬화/타임아웃 병목 가능"
  echo "[FIX] bash scripts/start_shadow_2worker.sh; 주기 8–12m 유지; BUNDLE_TIMEOUT=120 확인"
  EXIT_CODE=1
elif (( $(echo "$EV_VEL < 4.0" | bc -l 2>/dev/null || echo "0") )); then
  echo "[WARN] 목표(4.0/h) 미달"
  echo "[FIX] Shadow 병렬화 확인, 주기 최적화 검토"
  EXIT_CODE=0
else
  echo "[OK] 목표 달성"
  EXIT_CODE=0
fi
echo ""

# 2) AB p-value 분산
echo "## 2. AB p-value 분산"
PV=$(find var/evolution -name ab_eval.prom -newermt "-24 hours" \
     -exec awk '/^duri_ab_p_value[ {]/{print $2}' {} \; 2>/dev/null || true)
N=$(printf '%s\n' $PV | sed '/^$/d' | wc -l || echo 0)
U=$(printf '%s\n' $PV | sed '/^$/d' | sort -u | wc -l || echo 0)
echo "AB_p_samples: $N, unique_vals: $U"
if [ "${N:-0}" -eq 0 ]; then
  echo "[CAUSE] AB 샘플 없음 (24h 내 EV 없음 또는 ab_eval.prom 누락)"
  echo "[FIX] EV 생성 확인, evidence_bundle.sh 실행 확인"
  EXIT_CODE=1
elif [ "${U:-0}" -le 1 ]; then
  echo "[CAUSE] 상수화/캐시/입력 분기 실패"
  echo "[FIX] Δ7 경로 재검: EV별 JSONL 슬라이싱, RNG seed(ev_id) 강제, 캐시 파일 rm, 라벨(ev,n,build_unixtime) 확인"
  EXIT_CODE=1
else
  echo "[OK] 분산 확인 (고유값 ≥2)"
  EXIT_CODE=0
fi

# AB p-value 평균/표준편차
if [ "${N:-0}" -gt 0 ]; then
  PV_MEAN=$(printf '%s\n' $PV | sed '/^$/d' | awk '{sum+=$1; count++} END{if(count>0) print sum/count; else print 0}')
  PV_STD=$(printf '%s\n' $PV | sed '/^$/d' | awk -v m="$PV_MEAN" '{sum+=($1-m)^2; count++} END{if(count>1) print sqrt(sum/(count-1)); else print 0}')
  echo "  평균: $PV_MEAN, 표준편차: $PV_STD"
  if (( $(echo "$PV_MEAN < 0.05" | bc -l 2>/dev/null || echo "0") )); then
    echo "[OK] 통계적으로 유의미 (p < 0.05)"
  else
    echo "[WARN] 통계적으로 유의미하지 않음 (p >= 0.05)"
  fi
fi
echo ""

# 3) Shadow epoch
echo "## 3. Shadow Epoch 소요시간"
EPOCH_LOGS=$(grep -E "SHADOW_EPOCH_(START|END|DURATION)" var/logs/shadow.log 2>/dev/null | tail -10 || true)
if [ -z "$EPOCH_LOGS" ]; then
  echo "[WARN] Epoch 로그 부족"
  echo "[FIX] Shadow 실행 확인, shadow_duri_integration_final.sh END/DURATION 로그 확인"
else
  echo "최근 Epoch 로그:"
  echo "$EPOCH_LOGS" | tail -4 | sed 's/^/  /'
  
  # Duration 통계 (p50, p95)
  DURATIONS=$(echo "$EPOCH_LOGS" | grep "SHADOW_EPOCH_DURATION" | awk '{print $NF}' | sed 's/s$//' | sort -n)
  if [ -n "$DURATIONS" ]; then
    D_COUNT=$(echo "$DURATIONS" | wc -l)
    D_P50=$(echo "$DURATIONS" | awk -v n="$D_COUNT" 'NR==int(n*0.5+0.5) {print}')
    D_P95=$(echo "$DURATIONS" | awk -v n="$D_COUNT" 'NR==int(n*0.95+0.5) {print}')
    echo "  p50: ${D_P50}s, p95: ${D_P95}s (목표: p50≤360s, p95≤720s)"
    if [ "${D_P95:-999}" -gt 720 ]; then
      echo "[CAUSE] Shadow epoch 지연 (p95 > 12분)"
      echo "[FIX] 병렬화 확인, 타임아웃 확인, 병목 단계 분석"
    else
      echo "[OK] Shadow epoch 소요시간 정상"
    fi
  fi
fi
echo ""

# 4) DB 일관성
echo "## 4. DB 일관성"
if docker exec -e PGPASSWORD=postgres duri-postgres psql -U postgres -tc \
   "SELECT datname FROM pg_database WHERE datistemplate=false;" 2>/dev/null \
   | grep -qE 'duri_db'; then
  echo "[OK] DB: duri_db 존재"
else
  echo "[WARN] DB 스키마/이름 정합성 재확인"
  echo "[FIX] bash scripts/db_migrate_to_duri_db.sh 실행 또는 docker-compose.yml POSTGRES_DB 확인"
  EXIT_CODE=1
fi
echo ""

# 5) 메트릭 스크랩
echo "## 5. 메트릭 엔드포인트"
if bash scripts/scrape_metrics.sh 2>/dev/null | head -3 >/dev/null; then
  echo "[OK] 메트릭 엔드포인트 정상"
else
  echo "[WARN] metrics endpoint 확인 필요"
  echo "[FIX] shadow/metrics_exporter_enhanced.py 실행 확인, 포트 9109 확인"
fi
echo ""

# 6) 파일럿 프로세스 확인
echo "## 6. 파일럿 프로세스"
if pgrep -fa "pilot_24h\|shadow_parallel_worker" >/dev/null; then
  echo "[OK] 파일럿/워커 프로세스 실행 중"
  pgrep -fa "pilot_24h\|shadow_parallel_worker" | head -3 | sed 's/^/  /'
else
  echo "[WARN] 파일럿/워커 프로세스 없음"
  echo "[FIX] bash scripts/start_shadow_2worker.sh 또는 bash scripts/pilot_24h.sh 실행"
fi
echo ""

# 7) 최근 EV 생성 시간
echo "## 7. 최근 EV 생성 시간"
LAST_EV=$(find var/evolution -maxdepth 1 -type d -name "EV-*" -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1)
if [ -n "$LAST_EV" ]; then
  LAST_EV_TS=$(echo "$LAST_EV" | awk '{print int($1)}')
  LAST_EV_DIR=$(echo "$LAST_EV" | awk '{print $2}')
  NOW=$(date +%s)
  AGE=$((NOW - LAST_EV_TS))
  echo "최근 EV: $(basename "$LAST_EV_DIR")"
  echo "  생성 시간: ${AGE}s 전"
  if [ "$AGE" -gt 3600 ]; then
    echo "[WARN] 마지막 EV 생성 후 > 1시간 경과"
    echo "[FIX] 파일럿 프로세스 확인, Shadow 실행 확인"
  else
    echo "[OK] 최근 EV 생성 확인"
  fi
else
  echo "[WARN] EV 디렉터리 없음"
fi
echo ""

# 8) 라벨 무결성
echo "## 8. Label integrity"
bad=$(find var/evolution -name 'ab_eval.prom' -newermt '-2 hours' -exec grep -l '^duri_ab_p_value ' {} \; 2>/dev/null | wc -l)
if [ "$bad" -gt 0 ]; then
  echo "[FAIL] unlabeled p-lines: $bad (fix_legacy_prom.sh 실행 필요)"
  echo "[FIX] bash scripts/fix_legacy_prom.sh 실행 후 재확인"
  EXIT_CODE=2
else
  echo "[OK] no unlabeled p-lines in last 2h"
fi
echo ""

echo "=== Doctor End ==="
exit "${EXIT_CODE:-0}"

