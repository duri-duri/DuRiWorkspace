#!/usr/bin/env bash
# (1) 레거시 prom 정리 + 강제 재계산
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 레거시 prom 정리 + 강제 재계산 ==="
echo ""

# 2h 창 대상: 라벨 없는 p라인, 'SKIP', '--' 포함 라인 제거
echo "[1] 레거시 prom 정리 (2h 창)..."
REMOVED_COUNT=0
for f in $(find var/evolution -name "ab_eval.prom" -newermt "-2 hours" 2>/dev/null); do
    if grep -q '^duri_ab_p_value ' "$f" 2>/dev/null; then
        sed -i '/^duri_ab_p_value {/d; /SKIP/d; /--/d' "$f" 2>/dev/null || true
        REMOVED_COUNT=$((REMOVED_COUNT + 1))
    fi
done

# (B) Prometheus 룰용 메트릭 노출
mkdir -p var/metrics
echo "ab_unlabeled_detected ${REMOVED_COUNT}" > var/metrics/ab_unlabeled.prom 2>/dev/null || true

CLEANED_COUNT=$(find var/evolution -name "ab_eval.prom" -newermt "-2 hours" 2>/dev/null | wc -l)
echo "[OK] 처리된 파일: $CLEANED_COUNT, 제거된 라벨 없는 p라인: $REMOVED_COUNT"
echo ""

# (2) 파서의 '숫자만' 수집 확인 (드라이런)
echo "[2] 파서의 '숫자만' 수집 확인 (드라이런)..."
NUMERIC_COUNT=$(grep -h '^duri_ab_p_value{' var/evolution/*/ab_eval.prom 2>/dev/null \
  | awk '{print $NF}' | grep -E '^[0-9.]+(e-?[0-9]+)?$' 2>/dev/null | wc -l || echo "0")
echo "  숫자형 p-value 개수: $NUMERIC_COUNT"
echo ""

# (3) 2h 창 재집계
echo "[3] 2h 창 재집계:"
bash scripts/ab_pvalue_stats.sh "2 hours"
echo ""

# (4) EV/h 현황 + IO 병목 단서
echo "[4] EV/h 현황:"
bash scripts/ev_velocity.sh
echo ""

echo "[5] IO 병목 단서 (iostat):"
if command -v iostat >/dev/null 2>&1; then
    iostat -x 1 3 2>/dev/null | awk 'NR>3 && $1!~/^$/ {print $1,$14,$15}' | head -5 || echo "[INFO] iostat 실행 실패"
else
    echo "[INFO] iostat 없음"
fi
echo ""

# (1) 백필 정리: 24h/7d까지 완전 소거
echo "[6] 백필 정리 (24h/7d 완전 소거)..."
mkdir -p var/metrics
for win in "-24 hours" "-7 days"; do
  REMOVED=0
  # (2) glob 경합 방지: find -print0 | xargs -0 사용 (공백 안전)
  while IFS= read -r -d '' f; do
    if [ -n "$f" ] && [ -f "$f" ] && grep -q '^duri_ab_p_value ' "$f" 2>/dev/null; then
      # p라인만 제거 (안전)
      tmp="${f}.tmp"
      grep -v '^duri_ab_p_value ' "$f" > "$tmp" 2>/dev/null && mv "$tmp" "$f" 2>/dev/null || true
      REMOVED=$((REMOVED+1))
    fi
  done < <(find var/evolution -name "ab_eval.prom" -newermt "$win" -print0 2>/dev/null || true)
  
  # Prometheus 메트릭 노출
  win_clean=$(echo "$win" | tr -d ' ')
  echo "ab_unlabeled_removed_total{window=\"$win_clean\"} $REMOVED" >> var/metrics/ab_unlabeled.prom 2>/dev/null || true
  echo "  $win: 제거된 라벨 없는 p라인: $REMOVED"
done
echo "[OK] 백필 정리 완료"
echo ""

echo "=== 레거시 prom 정리 완료 ==="

