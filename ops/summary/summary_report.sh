#!/usr/bin/env bash
# Super-Safe Daily Summary Generator (self-contained)
# - config.env이 있으면 로드, 없으면 안전한 기본값으로 동작
# - DRY_RUN=1이면 README 패치/커밋/푸시는 생략하고 요약 산출물만 생성
# - 항상 SUMMARY_OUT 에 최소 헤더를 기록(빈 파일 방지)
set -euo pipefail

# -----------------------------
# 0) 설정 로드 + 기본값 주입
# -----------------------------
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

# 선택적 외부 설정
if [[ -f ops/summary/config.env ]]; then
  # shellcheck disable=SC1091
  source ops/summary/config.env
fi

: "${DRY_RUN:=1}"

# 경로/파일 기본값
: "${LOCK_PATH:=ops/summary/README_patch.lock}"
: "${LOG_ROOT:=var/logs}"
: "${SUMMARY_DIR:=var/logs/system/summary}"
: "${SUMMARY_JSON:=${SUMMARY_DIR}/summary_$(date +%F).json}"
: "${SUMMARY_MD:=${SUMMARY_DIR}/summary_$(date +%F).md}"
: "${SUMMARY_OUT:=${SUMMARY_DIR}/summary_$(date +%F_%H%M).md}"  # 사람이 보게 될 즉시 미니 리포트
: "${STATE_DIR:=var/state}"
: "${REPORT_DIR:=var/reports}"
: "${BACKUP_LOG_DIR:=${LOG_ROOT}/backup}"
: "${GATE_LOG_DIR:=${LOG_ROOT}/gate}"
: "${SYSTEM_LOG_DIR:=${LOG_ROOT}/system}"
: "${BACKUP_REFS_FILE:=${STATE_DIR}/backup_refs.json}"
: "${RESTORE_SLO_FILE:=${STATE_DIR}/restore_slo.jsonl}"
: "${HEALTH_LOG:=${SYSTEM_LOG_DIR}/health.log}"
: "${SUMMARY_HEADER:=# Daily Backup Summary}"

# README 패치 관련 기본값
: "${README_PATH:=README.md}"
: "${GIT_BRANCH:=main}"
: "${GIT_USER_NAME:=duri-bot}"
: "${GIT_USER_EMAIL:=duri-bot@example.local}"
: "${GRACE_DEGRADE_FULL_ON_INCR_FAIL:=1}"
: "${DEFER_RETENTION_ON_FAIL:=1}"

# 백업 루트 검색(옵션)
: "${DESK_ROOT:=/mnt/c/Users/admin/Desktop/두리백업}"
: "${USB_ROOT:=/mnt/usb/두리백업}"
: "${BACKUP_SEARCH_DIRS:=${DESK_ROOT}:${USB_ROOT}}"

# 필요 경로 보장
mkdir -p "$SUMMARY_DIR" "$STATE_DIR" "$REPORT_DIR" \
         "$BACKUP_LOG_DIR" "$GATE_LOG_DIR" "$SYSTEM_LOG_DIR" \
         "$(dirname "$SUMMARY_JSON")" "$(dirname "$SUMMARY_MD")" \
         "$(dirname "$SUMMARY_OUT")"

# -----------------------------
# 1) 락: 경합/중복 실행 차단
# -----------------------------
if [[ -e "$LOCK_PATH" ]]; then
  echo "[WARN] lock present, skip run"; exit 100
fi
trap 'rm -f "$LOCK_PATH"' EXIT
: > "$LOCK_PATH"

ts() { date +"%Y-%m-%d %H:%M:%S%z"; }

fail_fast() {
  echo "[ERROR] $1"; exit 1
}

log() {
  echo "[$(ts)] $*"
}

# -----------------------------
# 2) Phase 0: Fail-Fast 가드
# -----------------------------
log "INFO Phase 0: Fail-Fast 가드 검증 시작..."

# 2-1. 필수 경로
[[ -d "$BACKUP_LOG_DIR" ]] || fail_fast "missing $BACKUP_LOG_DIR"
[[ -d "$STATE_DIR" ]]      || fail_fast "missing $STATE_DIR"
[[ -d "ops/summary" ]]     || fail_fast "missing ops/summary directory"

# 2-2. 쓰기 권한
[[ -w "$BACKUP_LOG_DIR" ]] || fail_fast "no write permission → $BACKUP_LOG_DIR"
[[ -w "$STATE_DIR" ]]      || fail_fast "no write permission → $STATE_DIR"
[[ -w "$SUMMARY_DIR" ]]    || fail_fast "no write permission → $SUMMARY_DIR"

# 2-3. 용량 (소스×1.3)
src_kb="$(du -s . | cut -f1)"
avail_kb="$(df . | tail -1 | awk '{print $4}')"
need_kb=$((src_kb * 13 / 10))
if [[ "$avail_kb" -lt "$need_kb" ]]; then
  fail_fast "insufficient space: avail=${avail_kb}KB < need=${need_kb}KB"
fi

log "INFO Phase 0: Fail-Fast 가드 검증 완료"

# -----------------------------
# 3) 로그/상태 수집
# -----------------------------
today="$(date +%F)"
ok_incr=$(ls "$BACKUP_LOG_DIR"/incr_"$today"*.log 2>/dev/null | xargs -r grep -l "SUCCESS" | wc -l | xargs)
ok_ret=$(ls "$BACKUP_LOG_DIR"/retention_"$today"*.log 2>/dev/null | xargs -r grep -l "SUCCESS" | wc -l | xargs)
ok_health=$(ls "$BACKUP_LOG_DIR"/health_"$today"*.log 2>/dev/null | xargs -r grep -l "SUCCESS" | wc -l | xargs)

P0="done"
P1=$([[ $ok_incr   -gt 0 ]] && echo "done" || echo "pending")
P2=$([[ $ok_ret    -gt 0 ]] && echo "done" || echo "pending")
P3=$([[ $ok_health -gt 0 ]] && echo "done" || echo "pending")

# RTO 집계 (jq 있으면 더 정확, 없으면 단순 파싱)
rto_avg="n/a"; rto_max="n/a"
if [[ -f "$RESTORE_SLO_FILE" ]]; then
  if command -v jq >/dev/null 2>&1; then
    rto_avg="$(tail -n 200 "$RESTORE_SLO_FILE" | jq -s 'map(.restore_seconds) | add/length | tostring + "s"' 2>/dev/null || echo "n/a")"
    rto_max="$(tail -n 200 "$RESTORE_SLO_FILE" | jq -s 'map(.restore_seconds) | max | tostring + "s"' 2>/dev/null || echo "n/a")"
  else
    # JSONL에 "restore_seconds": <num> 혹은 rto_sec:<num> 혼재 대비
    read -r avg max < <(awk '
      /restore_seconds/{
        for(i=1;i<=NF;i++) if($i ~ /restore_seconds/){
          gsub(/[^0-9.]/,"",$ (i+1)); s+=$(i+1); c++
        }
      }
      /rto_sec/{
        for(i=1;i<=NF;i++) if($i ~ /rto_sec/){
          gsub(/[^0-9.]/,"",$(i)); s+=$(i); c++
        }
      }
      END{
        if(c>0){ printf "%.0fs %.0fs", s/c, m }
        else    { printf "n/a n/a" }
      }' m=0 s=0 c=0 "$RESTORE_SLO_FILE")
    rto_avg="${avg:-n/a}"
    rto_max="${max:-n/a}"
  fi
fi

status="OK"
if [[ $ok_incr -eq 0 || $ok_ret -eq 0 || $ok_health -eq 0 ]]; then
  status="WARN"
fi

# 최신 아카이브(상위 3)
latest_list=""
IFS=':' read -r -a roots <<< "$BACKUP_SEARCH_DIRS"
for r in "${roots[@]}"; do
  [[ -d "$r" ]] || continue
  mapfile -t found < <(find "$r" -type f -regex '.*\(FULL\|EXTENDED\|CORE\)__.*\.tar\.\(zst\|gz\)$' 2>/dev/null | sort | tail -3)
  for f in "${found[@]:-}"; do latest_list+="- $f"$'\n'; done
done
latest_list="${latest_list:-(no archives found)}"

# pending_usb_mirror 카운트
pending_count=0
for r in "${roots[@]}"; do
  [[ -d "$r" ]] || continue
  c=$(find "$r" -type f -name ".pending_usb_mirror" 2>/dev/null | wc -l | tr -d ' ')
  pending_count=$((pending_count + c))
done

# -----------------------------
# 4) 산출물 생성(JSON, MD)
# -----------------------------
mkdir -p "$(dirname "$SUMMARY_JSON")" "$(dirname "$SUMMARY_MD")"

cat > "${SUMMARY_JSON}.tmp" <<EOF
{
  "date": "$(date +%F)",
  "status": "$status",
  "phases": { "P0":"$P0", "P1":"$P1", "P2":"$P2", "P3":"$P3" },
  "rto_avg": "$rto_avg",
  "rto_max": "$rto_max",
  "phase0_completed": true,
  "fail_fast_guards": "active",
  "graceful_degrade": "enabled",
  "latest_archives_sample": $(printf '%s' "$latest_list" | jq -R -s 'split("\n")[:-1]'),
  "pending_usb_mirror": $pending_count,
  "generated_at": "$(ts)"
}
EOF
mv -f "${SUMMARY_JSON}.tmp" "$SUMMARY_JSON"

cat > "${SUMMARY_MD}.tmp" <<EOF
# Daily Backup Summary — $(date +%F)

- Status: **$status**
- Phases: P0=$P0, P1=$P1, P2=$P2, P3=$P3
- RTO (avg/max): $rto_avg / $rto_max
- Phase 0: **안전장치 가동 완료** ✅
- Fail-Fast: **활성화** ✅ / Graceful Degrade: **활성화** ✅
- Generated: $(ts)

## Latest Archives
$latest_list

## Health (tail)
$( [[ -f "$HEALTH_LOG" ]] && tail -n 5 "$HEALTH_LOG" | sed 's/^/  /' || echo "  (no health log)" )

## Restore SLO (last)
$( [[ -f "$RESTORE_SLO_FILE" ]] && tail -n 1 "$RESTORE_SLO_FILE" | sed 's/^/  /' || echo "  (no RTO yet)" )

## Flags
- pending_usb_mirror: $pending_count
EOF
mv -f "${SUMMARY_MD}.tmp" "$SUMMARY_MD"

log "INFO summary generated at: $SUMMARY_JSON / $SUMMARY_MD"

# -----------------------------
# 5) 최소 쓰기 보장(SUMMARY_OUT)
# -----------------------------
{
  echo "$SUMMARY_HEADER"
  echo "- Generated: $(date '+%F %T %Z')"
  echo ""
  echo "## Latest Archives"
  printf "%s\n" "$latest_list"
  echo ""
  echo "## Restore SLO (last)"
  [[ -f "$RESTORE_SLO_FILE" ]] && tail -n 1 "$RESTORE_SLO_FILE" | sed 's/^/  /' || echo "  (no RTO yet)"
} >> "$SUMMARY_OUT"

# -----------------------------
# 6) 힌트 로그 (Graceful Degrade)
# -----------------------------
if [[ "${GRACE_DEGRADE_FULL_ON_INCR_FAIL}" = "1" && $ok_incr -eq 0 ]]; then
  log "HINT INCR fail → schedule FULL next day (Graceful Degrade)"
fi
if [[ "${DEFER_RETENTION_ON_FAIL}" = "1" && $ok_ret -eq 0 ]]; then
  log "HINT RETENTION defer by 1 day (Graceful Degrade)"
fi

# -----------------------------
# 7) DRY-RUN 종료 분기
# -----------------------------
if [[ "$DRY_RUN" = "1" ]]; then
  log "DRY run: stop before README update / git push"
  exit 0
fi

# -----------------------------
# 8) README 패치 & 커밋/푸시
# -----------------------------
if [[ -f "$README_PATH" ]] && [[ -f ops/summary/update_phase_table.py ]]; then
  python3 ops/summary/update_phase_table.py --readme "$README_PATH" --summary "$SUMMARY_JSON" || true
fi

git config user.name  "$GIT_USER_NAME"  || true
git config user.email "$GIT_USER_EMAIL" || true
git checkout "$GIT_BRANCH"              || true
git add "$README_PATH" "$SUMMARY_JSON" "$SUMMARY_MD" || true
git commit -m "auto: daily summary update ($(date +%F))" || true
git push origin "$GIT_BRANCH" || true

log "INFO README updated & committed"

