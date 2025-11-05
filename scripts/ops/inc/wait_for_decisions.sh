#!/usr/bin/env bash
# Wait for Decisions - 결정 파일 가용성 대기
# Purpose: 결정 파일이 유효한 상태가 될 때까지 대기
# Usage: wait_for_decisions <file> <min_count> <max_age_sec>

set -euo pipefail

f="${1:-var/audit/decisions.ndjson}"
min="${2:-1}"
max_age="${3:-86400}"

WORK="${WORK:-/home/duri/DuRiWorkspace}"
if [[ ! "$f" =~ ^/ ]]; then
  f="${WORK}/${f}"
fi

for i in $(seq 1 30); do
  if [[ ! -f "$f" ]]; then
    sleep 1
    continue
  fi
  
  # 스키마 검증 및 24h 내 결정 카운트
  cnt=$(jq -r '
    select(type=="object" and .ts and .decision) 
    | select(.decision | IN("GO","NO-GO","REVIEW","HOLD","HEARTBEAT","APPROVED","CONTINUE"))
    | ( .ts | fromdateiso8601 ) 
    | select(. > (now - '"$max_age"'))
  ' "$f" 2>/dev/null | wc -l | tr -d " ")
  
  if [[ "${cnt:-0}" -ge "$min" ]]; then
    exit 0
  fi
  
  sleep 1
done

echo "[ERR] decisions not ready (min=$min within 30s)" >&2
exit 1

