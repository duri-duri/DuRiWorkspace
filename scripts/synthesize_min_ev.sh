#!/usr/bin/env bash
set -euo pipefail

ROOT="var/evolution"

NOW_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mk_ev () {
  local ev_id="$1"
  local dir="$ROOT/$ev_id"
  mkdir -p "$dir"
  local f="$dir/evolution.$ev_id.jsonl"
  # EV당 A/B 2라인. metric.value를 살짝 다르게 줘서 p가 달라질 여지 확보.
  cat > "$f" <<JSON
{"schema_version":"1","ts":"$NOW_UTC","cycle_id":"$ev_id","variant":"A","metric":{"name":"loss","value":0.321},"n":1}
{"schema_version":"1","ts":"$NOW_UTC","cycle_id":"$ev_id","variant":"B","metric":{"name":"loss","value":0.123},"n":1}
JSON
  echo "[OK] synthesized $f" 1>&2
}

# 서로 다른 두 개의 EV 생성 (서로 다른 seed 경로 보장)
EVA="EV-$(date -u +%Y%m%d-%H%M%S)-SYN01"
EVB="EV-$(date -u +%Y%m%d-%H%M%S)-SYN02"
mk_ev "$EVA"
sleep 1
mk_ev "$EVB"
# stdout에는 **ID만** 출력 → command substitution 안전
printf "%s %s\n" "$EVA" "$EVB"

