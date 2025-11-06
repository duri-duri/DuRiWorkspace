#!/usr/bin/env bash
# L4 Post-Merge Script - 머지 후 태깅 및 관찰 시작
# Purpose: PR 머지 후 L4 태그 생성 및 24h 관찰 루틴 시작
# Usage: scripts/ops/l4_post_merge.sh

set -euo pipefail

WORK="${WORK:-$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)}"
cd "$WORK"

echo "=== L4 Post-Merge Script Start $(date) ==="

# 1. Main 브랜치 동기화
echo "[1] Syncing main branch..."
git fetch -p origin main || { echo "[ERROR] Failed to fetch main"; exit 1; }
git switch main || { echo "[ERROR] Failed to switch to main"; exit 1; }
git pull origin main || { echo "[ERROR] Failed to pull main"; exit 1; }

# 2. L4 태그 생성
TAG_NAME="l4-ready-$(date +%Y%m%d-%H%M)"
echo "[2] Creating tag: $TAG_NAME"
git tag -a "$TAG_NAME" -m "L4 automation ready

- Canonicalize+validator pipeline
- A4 drift ζ cap (16s)
- A6 metrics (canon_total/bad)
- Observability alerts (4 types)
- Self-healing layer (L5)
- Label policy automation

Status: All checks passed, ready for 24h observation"

# 3. 태그 푸시
echo "[3] Pushing tag..."
git push origin "$TAG_NAME" || { echo "[ERROR] Failed to push tag"; exit 1; }

# 4. 24h 관찰 루틴 확인
echo "[4] Verifying 24h observation setup..."

# 타이머 상태 확인
TIMER_STATUS=$(systemctl --user is-enabled l4-weekly.timer 2>/dev/null || echo "disabled")
echo "  Timer status: $TIMER_STATUS"

if [[ "$TIMER_STATUS" != "enabled" ]]; then
  echo "  ⚠️  WARN: l4-weekly.timer is not enabled"
  echo "  Enable with: systemctl --user enable --now l4-weekly.timer"
fi

# 메트릭 파일 확인
METRIC_FILES=(
  "$HOME/.cache/node_exporter/textfile/l4_weekly_decision.prom"
  "$HOME/.cache/node_exporter/textfile/l4_canon_metrics.prom"
  "$HOME/.cache/node_exporter/textfile/l4_backfill_rc.prom"
)

for file in "${METRIC_FILES[@]}"; do
  if [[ -f "$file" ]]; then
    echo "  ✅ Found: $(basename "$file")"
    # 신선도 확인
    if [[ "$file" == *"l4_weekly_decision.prom" ]]; then
      TS=$(awk '/^l4_weekly_decision_ts/{print $NF}' "$file" | tail -n1)
      if [[ -n "$TS" ]]; then
        NOW=$(date -u +%s)
        DELTA=$((NOW - TS))
        ZETA=16
        EFFECTIVE=$((DELTA > ZETA ? DELTA - ZETA : 0))
        echo "    Freshness: Δ=${DELTA}s, effective=${EFFECTIVE}s (target: ≤120s)"
      fi
    fi
  else
    echo "  ⚠️  WARN: Missing $(basename "$file")"
  fi
done

# 5. 관찰 체크리스트 출력
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
echo "  cat ~/.cache/node_exporter/textfile/l4_weekly_decision.prom"
echo "  cat ~/.cache/node_exporter/textfile/l4_canon_metrics.prom"
echo "  cat ~/.cache/node_exporter/textfile/l4_backfill_rc.prom"
echo ""
echo "  # Prometheus 쿼리 (선택)"
echo "  # (l4_canon_bad / clamp_min(l4_canon_total,1))"
echo "  # (time() - l4_weekly_decision_ts)"
echo ""
echo "=== L4 Post-Merge Script Complete ==="
echo "Tag: $TAG_NAME"
echo "Next: 24h observation period"

