#!/usr/bin/env bash
set -euo pipefail
export COMPOSE_PROJECT_NAME=duriworkspace
cd /home/duri/DuRiWorkspace

EXP="smoke_$(date +%F_%H%M%S)"
echo "[coach smoke] exp=${EXP}"

docker compose exec -T duri_control bash -lc '
  set -euo pipefail
  IN_TSV=/tmp/coach_input_$RANDOM.tsv
  OUT_JSON="/tmp/coach_'"$EXP"'.json"

  # TSV 리터럴: 탭 문자 유지, JSON/SQL 안전
  cat > "$IN_TSV" <<'"'TSV'"'
1	지난 10분 이벤트 수 숫자만	{"min":0,"type":"int"}	{"type":"sql","spec":"SELECT COUNT(*) FROM v_feedback_events_clean WHERE ts >= NOW() - INTERVAL '\''10 minutes'\''"}
TSV

  python /app/tools/coach_runner.py --exp "'"$EXP"'" --input "$IN_TSV" --out "$OUT_JSON"
  python /app/tools/coach_ingest.py --exp "'"$EXP"'" --input "$OUT_JSON"
'

# DB로 판정하고 비정상 시 non-zero exit
RECENT_GOOD=$(docker compose exec -T duri-postgres psql -U duri -d duri -tAc \
  "SELECT COUNT(*) FROM coach_results WHERE exp_id <> '' AND ts >= NOW() - INTERVAL '10 minutes';")

echo "recent_good=${RECENT_GOOD}"

# 결과 확인
docker compose exec -T duri-postgres psql -U duri -d duri -c \
"SELECT id,exp_id,item_id,score,latency_ms,ts FROM coach_results ORDER BY id DESC LIMIT 5;"

# 비정상 시 non-zero exit
if [ "$RECENT_GOOD" -ge 1 ]; then
  echo "✅ E2E 성공: recent_good=${RECENT_GOOD}"
  exit 0
else
  echo "❌ E2E 실패: recent_good=${RECENT_GOOD}"
  exit 1
fi

# 성공/실패 카운터 업데이트 (webhook으로)
if [ "$RECENT_GOOD" -ge 1 ]; then
  echo "✅ E2E 성공: recent_good=${RECENT_GOOD}"
  # 성공 카운터 증가 (webhook으로)
  curl -s -X POST http://localhost:8083/metrics/smoke_success || true
  exit 0
else
  echo "❌ E2E 실패: recent_good=${RECENT_GOOD}"
  # 실패 카운터 증가 (webhook으로)
  curl -s -X POST http://localhost:8083/metrics/smoke_failure || true
  exit 1
fi
