#!/usr/bin/env bash
set -euo pipefail
ts=$(date +%Y%m%d-%H%M%S)
docker compose logs --since=2h aggregation_worker > proof_${ts}_agg.log
docker compose exec duri-postgres psql -U duri -d duri -c \
"SELECT model_id, decision, reason, decision_ts 
 FROM v_promotion_latest ORDER BY decision_ts DESC" > proof_${ts}_decisions.txt
docker compose exec duri-postgres psql -U duri -d duri -c \
"SELECT meta_model_id model, track, COUNT(*) n 
 FROM v_feedback_events_clean 
 WHERE ts>=NOW()-INTERVAL '10 minutes' AND track IN ('cand','prod')
 GROUP BY 1,2 ORDER BY 1,2" > proof_${ts}_window.txt
tar -czf proof_bundle_${ts}.tar.gz proof_${ts}_*.*
echo "created: proof_bundle_${ts}.tar.gz"
