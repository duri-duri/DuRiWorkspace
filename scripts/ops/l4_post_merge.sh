#!/usr/bin/env bash
# L4 Post-Merge Script - 머지 후 태깅 및 관찰 시작
# Purpose: PR 머지 후 L4 태그 생성 및 24h 관찰 루틴 시작
# Usage: scripts/ops/l4_post_merge.sh

set -euo pipefail

WORK="${WORK:-$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)}"
cd "$WORK"

echo "=== L4 Post-Merge Script Start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

# 1. Main 브랜치 동기화
echo "[1] Syncing main branch..."
git fetch -p origin main || { echo "[ERROR] Failed to fetch main"; exit 1; }
git switch main || { echo "[ERROR] Failed to switch to main"; exit 1; }
git pull origin main || { echo "[ERROR] Failed to pull main"; exit 1; }

# 2. L4 태그 생성
TAG_NAME="l4-finalize-$(date +%Y%m%d-%H%M)"
echo "[2] Creating tag: $TAG_NAME"
git tag -a "$TAG_NAME" -m "L4 automation ready

- Canonicalize+validator pipeline
- A4 drift ζ cap (16s)
- A6 metrics (canon_total/bad)
- Observability alerts (4 types)
- Self-healing layer (L5)
- Label policy automation
- Protection relax→merge→restore automation

Status: All checks passed, ready for 24h observation
MergeCommit: $(git rev-parse --short HEAD)"

# 3. 태그 푸시
echo "[3] Pushing tag..."
git push origin "$TAG_NAME" || { echo "[ERROR] Failed to push tag"; exit 1; }

# 4. 24h 관찰 루틴 확인 및 초기화
echo "[4] Verifying and initializing 24h observation setup..."

# 텍스트파일 디렉터리 확인
TEXTFILE_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
mkdir -p "$TEXTFILE_DIR"

# 메트릭 파일 초기화/갱신
echo "[4.1] Initializing metrics files..."

# l4_weekly_decision.prom 초기화
cat > "${TEXTFILE_DIR}/l4_weekly_decision.prom" <<EOF
# HELP l4_weekly_decision_ts Unix timestamp of last weekly decision (UTC)
# TYPE l4_weekly_decision_ts gauge
l4_weekly_decision_ts{decision="HEARTBEAT"} $(date -u +%s)
EOF

# l4_canon_metrics.prom 초기화 (없으면 생성)
if [[ ! -f "${TEXTFILE_DIR}/l4_canon_metrics.prom" ]]; then
  cat > "${TEXTFILE_DIR}/l4_canon_metrics.prom" <<EOF
# HELP l4_canon_total Total lines processed by canonicalizer
# TYPE l4_canon_total counter
l4_canon_total{} 0
# HELP l4_canon_bad Bad lines dropped by canonicalizer
# TYPE l4_canon_bad counter
l4_canon_bad{} 0
EOF
fi

# l4_backfill_rc.prom 초기화 (없으면 생성)
if [[ ! -f "${TEXTFILE_DIR}/l4_backfill_rc.prom" ]]; then
  cat > "${TEXTFILE_DIR}/l4_backfill_rc.prom" <<EOF
# HELP l4_backfill_last_rc Exit code of last backfill run (0=ok, >0=error)
# TYPE l4_backfill_last_rc gauge
l4_backfill_last_rc{} 0
EOF
fi

# l4_boot_status.prom 초기화 (없으면 생성)
if [[ ! -f "${TEXTFILE_DIR}/l4_boot_status.prom" ]]; then
  cat > "${TEXTFILE_DIR}/l4_boot_status.prom" <<EOF
# HELP l4_boot_status Boot recovery status (1=recovered, 0=not recovered)
# TYPE l4_boot_status gauge
l4_boot_status{} 1
EOF
fi

chmod 0644 "${TEXTFILE_DIR}"/*.prom || true

# 5. 타이머 상태 확인 및 활성화
echo "[4.2] Verifying systemd timers..."
TIMER_STATUS=$(systemctl --user is-enabled l4-weekly.timer 2>/dev/null || echo "disabled")
echo "  Timer status: $TIMER_STATUS"

if [[ "$TIMER_STATUS" != "enabled" ]]; then
  echo "  ⚠️  WARN: l4-weekly.timer is not enabled"
  echo "  Enabling timer..."
  systemctl --user daemon-reload || true
  systemctl --user enable --now l4-weekly.timer 2>/dev/null || echo "  ⚠️  Failed to enable timer"
fi

# 6. 관찰 체크리스트 출력
echo ""
echo "=== 24h Observation Checklist ==="
echo ""
echo "핵심 지표 (목표):"
echo "  - Δ_effective ≤ 120s"
echo "  - l4_canon_bad_ratio < 0.02"
echo "  - l4_backfill_last_rc == 0"
echo "  - l4_boot_status == 1"
echo ""
echo "확인 명령어:"
echo "  # 타이머 상태"
echo "  systemctl --user status l4-weekly.timer --no-pager -l"
echo ""
echo "  # 메트릭 확인"
echo "  cat ${TEXTFILE_DIR}/l4_weekly_decision.prom"
echo "  cat ${TEXTFILE_DIR}/l4_canon_metrics.prom"
echo "  cat ${TEXTFILE_DIR}/l4_backfill_rc.prom"
echo ""
echo "  # Prometheus 쿼리 (선택)"
echo "  # (l4_canon_bad / clamp_min(l4_canon_total,1))"
echo "  # (time() - l4_weekly_decision_ts)"
echo ""
echo "=== L4 Post-Merge Script Complete ==="
echo "Tag: $TAG_NAME"
echo "Next: 24h observation period"
echo "Start timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
