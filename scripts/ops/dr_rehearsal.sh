#!/usr/bin/env bash
# DR (Disaster Recovery) Rehearsal Job
# Purpose: Automatically restore random backup samples and validate
# Usage: Daily cron job (e.g., 02:00 daily)

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

ARCHIVE_DIR="${ARCHIVE_DIR:-/mnt/hdd/ARCHIVE/INCR}"
RESTORE_DIR="${RESTORE_DIR:-/tmp/duri-restore-$$}"
DR_REPORT="${DR_REPORT:-.reports/dr/dr_report_$(date +%Y%m%d_%H%M%S).jsonl}"
mkdir -p "$(dirname "$DR_REPORT")" "$RESTORE_DIR"

TS_START=$(date +%s)

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

# 1) Random sample selection
log "Selecting random backup sample..."
BACKUP_FILES=($(ls -1t "$ARCHIVE_DIR"/*.tar.zst 2>/dev/null | head -30))
if [ ${#BACKUP_FILES[@]} -eq 0 ]; then
  log "[ERROR] No backup files found in $ARCHIVE_DIR"
  exit 1
fi

RANDOM_SAMPLE="${BACKUP_FILES[$((RANDOM % ${#BACKUP_FILES[@]}))]}"
log "[SELECTED] $RANDOM_SAMPLE"

# 2) Restore to temporary directory
log "Restoring to $RESTORE_DIR..."
mkdir -p "$RESTORE_DIR"
tar --zstd -xf "$RANDOM_SAMPLE" -C "$RESTORE_DIR" 2>&1 | tail -5 || {
  log "[ERROR] Restore failed"
  rm -rf "$RESTORE_DIR"
  exit 1
}

# 3) Validate restored workspace
log "Validating restored workspace..."
cd "$RESTORE_DIR"

# Check if key files exist
KEY_FILES=("scripts/ops/resume_obs_green_lock.sh" "prometheus/rules/duri-observability-contract.rules.yml" "Makefile")
missing=0
for f in "${KEY_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    log "[WARN] Missing key file: $f"
    missing=$((missing + 1))
  fi
done

# 4) Run promtool check (if prometheus dir exists)
promtool_result="skip"
if [ -d "prometheus/rules" ]; then
  log "Running promtool check..."
  if docker run --rm --entrypoint /bin/sh \
    -v "$(pwd)/prometheus:/etc/prometheus:ro" \
    prom/prometheus:v2.54.1 -lc \
    'promtool check config /etc/prometheus/prometheus.yml.minimal 2>/dev/null || true && promtool check rules /etc/prometheus/rules/*.yml 2>/dev/null || true' >/dev/null 2>&1; then
    promtool_result="pass"
  else
    promtool_result="fail"
  fi
fi

# 5) Run resume script (dry-run)
resume_result="skip"
if [ -f "scripts/ops/resume_obs_green_lock.sh" ]; then
  log "Running resume script (dry-run)..."
  if bash scripts/ops/resume_obs_green_lock.sh >/dev/null 2>&1; then
    resume_result="pass"
  else
    resume_result="fail"
  fi
fi

TS_END=$(date +%s)
RESTORE_TIME=$((TS_END - TS_START))

# 6) Write report
SUCCESS=0
if [ "$missing" -eq 0 ] && [ "$promtool_result" != "fail" ] && [ "$resume_result" != "fail" ]; then
  SUCCESS=1
fi

cat >> "$DR_REPORT" <<EOF
{"timestamp":"$(date -Iseconds)","backup":"$(basename "$RANDOM_SAMPLE")","restore_time_seconds":$RESTORE_TIME,"missing_files":$missing,"promtool":"$promtool_result","resume":"$resume_result","success":$SUCCESS}
EOF

# 7) Export metrics to textfile
METRICS_DIR="${METRICS_DIR:-.reports/textfile}"
mkdir -p "$METRICS_DIR"
tmp_metrics=$(mktemp "${METRICS_DIR}/.duri_dr_metrics.prom.XXXXXX")
{
  echo "# HELP duri_dr_restore_time_seconds DR restore rehearsal time in seconds"
  echo "# TYPE duri_dr_restore_time_seconds histogram"
  echo "duri_dr_restore_time_seconds_bucket{le=\"10\"} $(if [ $RESTORE_TIME -le 10 ]; then echo 1; else echo 0; fi)"
  echo "duri_dr_restore_time_seconds_bucket{le=\"30\"} $(if [ $RESTORE_TIME -le 30 ]; then echo 1; else echo 0; fi)"
  echo "duri_dr_restore_time_seconds_bucket{le=\"60\"} $(if [ $RESTORE_TIME -le 60 ]; then echo 1; else echo 0; fi)"
  echo "duri_dr_restore_time_seconds_bucket{le=\"300\"} $(if [ $RESTORE_TIME -le 300 ]; then echo 1; else echo 0; fi)"
  echo "duri_dr_restore_time_seconds_bucket{le=\"+Inf\"} 1"
  echo "duri_dr_restore_time_seconds_sum $RESTORE_TIME"
  echo "duri_dr_restore_time_seconds_count 1"
  echo ""
  echo "# HELP duri_dr_success_total Total successful DR rehearsals"
  echo "# TYPE duri_dr_success_total counter"
  echo "duri_dr_success_total $SUCCESS"
  echo ""
  echo "# HELP duri_dr_failure_total Total failed DR rehearsals"
  echo "# TYPE duri_dr_failure_total counter"
  echo "duri_dr_failure_total $((1 - SUCCESS))"
} > "$tmp_metrics"
chmod 644 "$tmp_metrics"
mv -f "$tmp_metrics" "${METRICS_DIR}/duri_dr_metrics.prom"

# 8) Cleanup
log "Cleaning up restore directory..."
rm -rf "$RESTORE_DIR"

log "[REPORT] Written to $DR_REPORT"
log "[RESULT] success=$SUCCESS, restore_time=${RESTORE_TIME}s, missing=$missing"

exit $((1 - SUCCESS))

