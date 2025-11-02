#!/usr/bin/env bash
# DuRi 관찰 스택 복원 스크립트
# 사용법: bash scripts/ops/resume_obs_green_lock.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

echo "=== DuRi 관찰 스택 복원 시작 ==="
echo ""

# 1. Git 상태 확인
echo "[1/5] Git 상태 확인..."
git fetch origin 2>/dev/null || echo "[WARN] git fetch 실패 (계속 진행)"
BRANCH="fix/p-sigma-writer"
if git branch --show-current | grep -q "$BRANCH"; then
  echo "✅ 현재 브랜치: $BRANCH"
else
  echo "[INFO] 브랜치 전환: $BRANCH"
  git checkout "$BRANCH" 2>/dev/null || echo "[WARN] 브랜치 전환 실패 (계속 진행)"
fi
git pull origin "$BRANCH" 2>/dev/null || echo "[WARN] git pull 실패 (계속 진행)"
echo ""

# 2. 백업 확인
echo "[2/5] 백업 파일 확인..."
LATEST_BACKUP=$(ls -1t /mnt/hdd/ARCHIVE/INCR/INCR__*.tar.zst 2>/dev/null | head -1)
if [ -n "$LATEST_BACKUP" ]; then
  SIZE=$(ls -lh "$LATEST_BACKUP" | awk '{print $5}')
  echo "✅ 최신 백업: $(basename "$LATEST_BACKUP") ($SIZE)"
else
  echo "[WARN] 백업 파일을 찾을 수 없음"
fi
echo ""

# 3. 주요 파일 확인
echo "[3/5] 주요 파일 확인..."
FILES=(
  ".git/hooks/pre-receive"
  "scripts/ops/reload_safe.sh"
  "scripts/ops/textfile_heartbeat.sh"
  "prometheus/rules/duri-observability-contract.rules.yml"
)
ALL_OK=true
for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    echo "  ✅ $f"
  else
    echo "  ❌ $f (없음)"
    ALL_OK=false
  fi
done
echo ""

# 4. Prometheus 상태 확인
echo "[4/5] Prometheus 상태 확인..."
if curl -sf --max-time 3 http://localhost:9090/-/ready >/dev/null 2>&1; then
  echo "✅ Prometheus: 준비됨"
  
  # Recording rule 확인
  GREEN_COUNTER=$(curl -sf --max-time 3 --get 'http://localhost:9090/api/v1/query' \
    --data-urlencode 'query=duri_obs_green_run_counter' 2>/dev/null | \
    jq -r '.data.result[0].value[1] // "0"' 2>/dev/null || echo "0")
  echo "  📊 duri_obs_green_run_counter: $GREEN_COUNTER"
else
  echo "❌ Prometheus: 응답 없음 (Docker 컨테이너 확인 필요)"
fi
echo ""

# 5. Textfile heartbeat 확인
echo "[5/5] Textfile heartbeat 확인..."
if [ -f "reports/textfile/duri_textfile_heartbeat.prom" ]; then
  TS=$(grep -v '^#' reports/textfile/duri_textfile_heartbeat.prom | awk '{print $2}' | head -1)
  AGE=$(( $(date +%s) - ${TS:-0} ))
  if [ "$AGE" -lt 600 ]; then
    echo "✅ Heartbeat: 활성 (${AGE}초 전 업데이트)"
  else
    echo "⚠️  Heartbeat: 오래됨 (${AGE}초 전 업데이트)"
  fi
else
  echo "⚠️  Heartbeat 파일 없음 (cron job 확인 필요)"
fi
echo ""

# 최종 상태
echo "=== 복원 완료 ==="
if [ "$ALL_OK" = true ]; then
  echo "✅ 모든 주요 파일이 존재합니다."
else
  echo "⚠️  일부 파일이 누락되었습니다. 백업 확인을 권장합니다."
fi
echo ""
echo "📋 다음 단계:"
echo "  1. Prometheus 상태 확인: curl -s http://localhost:9090/-/ready"
echo "  2. cron job 설정 (선택): */5 * * * * cd $ROOT && bash scripts/ops/textfile_heartbeat.sh"
echo "  3. 상태 문서 확인: cat docs/ops/OBS_GREEN_LOCK_STATUS.md"
echo ""

