#!/usr/bin/env bash
set -euo pipefail

# === Tight SLO defaults ===
P95_MS="${P95_MS:-200}"
P99_MS="${P99_MS:-300}"
EXCEED_MAX="${EXCEED_MAX:-0.02}"   # 2%
CONF="${CONF:-0.95}"               # 95%
PROM_URL="${PROM_URL:-http://localhost:9090}"
WIN="${WIN:-10m}"
STEP="${STEP:-15s}"

TS="$(date +%F_%H%M%S)"
OUT="$HOME/backup_logs/pre15_${TS}"
mkdir -p "$OUT"

log(){ printf "%s %s\n" "$(date +%F_%T)" "$*" | tee -a "$OUT/summary.log"; }

log "=== Day1-10 산출물 구조 점검 ==="
ls -la DuRiCore_backup_20250805_113147/ \
  | grep -E 'DAY([1-9]|10)_COMPLETION_REPORT\.md|PROGRESS|RESTART_GUIDE' \
  | tee "$OUT/day_reports.list"
for d in {1..10}; do
  test -f "DuRiCore_backup_20250805_113147/DAY${d}_COMPLETION_REPORT.md" \
    && echo "OK DAY$d" || echo "MISS DAY$d"
done | tee "$OUT/day_ok.txt"

log "--- 누락 Day 체크(있으면 보강 필요) ---"
grep -v '^OK' "$OUT/day_ok.txt" || true

log "=== Canary 툴체인 존재/권한 점검 ==="
ls -la tools/ | grep -E '(canary|annotate|guard|pipeline)' | tee "$OUT/tools.list"
test -f tools/canary_guard.py && test -x tools/canary_pipeline.sh && echo OK_canary_tools >> "$OUT/flags"

log "=== Observability 구성 파일 점검 ==="
ls -la ops/observability/ | tee "$OUT/obs_tree.txt"
for f in prometheus.yml otel_init.py metrics_server.py; do
  test -f "ops/observability/$f" && echo "OK $f" || echo "MISS $f"
done | tee "$OUT/obs_files.txt"
ls -la ops/observability/rules | tee "$OUT/rules_tree.txt" || true

log "=== Cron 스케줄 검증(Phase1) ==="
crontab -l | tee "$OUT/cron.txt"
# Sunday 15:00 full — robust regex check
if grep -Eq '^[[:space:]]*0[[:space:]]+15[[:space:]]+\*[[:space:]]+\*[[:space:]]+(0|7|sun|SUN|Sun)[[:space:]]+[^#]*\/home\/duri\/DuRiWorkspace\/scripts\/duri_backup_phase1\.sh([[:space:]]|$).*([[:space:]]|^)full([[:space:]]|$)' "$OUT/cron.txt"; then
  echo OK_full15h >> "$OUT/flags"
else
  echo MISS_full15h >> "$OUT/flags"
  echo "FAIL: Sunday 15:00 full backup cron not found" | tee -a "$OUT/summary.log"
  PASS=0
fi

log "=== Canary Guard Tight SLO Dry-run ==="
cat > "$OUT/slo.cfg" <<CFG
P95_MS=$P95_MS
P99_MS=$P99_MS
EXCEED_MAX=$EXCEED_MAX
CONF=$CONF
PROM_URL=$PROM_URL
WIN=$WIN
STEP=$STEP
CFG

python3 tools/canary_guard.py \
  --prom-url "$PROM_URL" \
  --window "$WIN" --step "$STEP" \
  --p95-slo-ms "$P95_MS" --p99-slo-ms "$P99_MS" \
  --min-exceed-ratio "$EXCEED_MAX" --confidence "$CONF" \
  > "$OUT/canary_tight.txt" 2>&1 || echo "DRYRUN_WARN" >> "$OUT/flags"

log "=== 백업 로그 최신 상태 스냅샷 ==="
for f in full.log incr.log retention.log health.log; do
  test -f "$HOME/backup_logs/$f" && tail -n 50 "$HOME/backup_logs/$f" > "$OUT/tail_$f" || true
done

log "=== 디스크/메모리 여유 ==="
TARGET="${TARGET_FS:-/}"  # 필요시: export TARGET_FS=/mnt/c
usage=$(LANG=C df -P "$TARGET" | awk 'NR==2{gsub("%","",$5); print $5+0}')
echo "disk_usage_percent(${TARGET})=${usage}%"
if [ "${usage:-0}" -ge 85 ]; then
  echo "WARN: Disk usage high on ${TARGET} (${usage}%)" | tee -a "$OUT/summary.log"
fi
df -h > "$OUT/df.txt"
free -h > "$OUT/mem.txt" || true
top -b -n1 | head -40 > "$OUT/top.txt"

log "=== 합격 기준 자동평가 (Tight) ==="
PASS=1

# (1) Day 보고서 1~10 모두 존재
if [ "$(grep -c '^OK DAY' "$OUT/day_ok.txt")" -ne 10 ]; then
  echo "FAIL: DAY reports missing" | tee -a "$OUT/summary.log"
  PASS=0
fi

# (2) Canary 툴체인
grep -q 'OK_canary_tools' "$OUT/flags" || { echo "FAIL: Canary tools" | tee -a "$OUT/summary.log"; PASS=0; }

# (3) 15:00 풀백업 스케줄
grep -q 'OK_full15h' "$OUT/flags" || { echo "FAIL: 15:00 cron" | tee -a "$OUT/summary.log"; PASS=0; }

# (4) 리소스 여유 — 디스크 85% 이하 권고 (경고만)

# (5) DRYRUN 경고만 플래그
grep -q 'DRYRUN_WARN' "$OUT/flags" && echo "WARN: Canary dry-run warnings" | tee -a "$OUT/summary.log" || true

if [ $PASS -eq 1 ]; then
  log ">>> PRE-15 CHECK (TIGHT): PASS"
  exit 0
else
  log ">>> PRE-15 CHECK (TIGHT): FAIL"
  exit 1
fi






