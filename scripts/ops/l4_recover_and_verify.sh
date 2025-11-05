#!/usr/bin/env bash
# L4 Recover and Verify - 재부팅 후 자동 복구 스크립트
# Purpose: 재부팅/전원 복구 후 L4 루프를 최소한의 조치로 복구
# Usage: ~/bin/l4_recover_and_verify.sh (자동 실행 또는 수동 실행)

set -euo pipefail

LOG="/tmp/l4_recover.$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

echo ">>> L4 복구 시작: $(date)"

# 0. 변수
WORK="/home/duri/DuRiWorkspace"
CANON="${WORK}/scripts/ops/inc/l4_canonicalize_ndjson.sh"
VALID="${WORK}/scripts/ops/l4_validation.sh"
REBOOT_CHECK="${WORK}/scripts/ops/l4_reboot_survival_check.sh"
SHADOW_UNIT="l4-shadow-replay.service"
TIMERS=("l4-daily" "l4-daily-quick" "l4-shadow-replay" "l4-weekly" "l4-canonicalize")

# 1. linger 보장
echo "[1] enable-linger"
loginctl enable-linger "$(whoami)" 2>/dev/null || sudo loginctl enable-linger "$(whoami)" 2>/dev/null || echo "linger ok or no permission"

# 2. systemd user 데몬 리로드
echo "[2] daemon-reload"
systemctl --user daemon-reload || { echo "[ERROR] daemon-reload failed"; exit 1; }

# 3. 모든 L4 타이머/서비스 enable & start
echo "[3] enable & start timers/services"
for t in "${TIMERS[@]}"; do
  systemctl --user enable --now "${t}.timer" 2>/dev/null || echo "  ⚠️  ${t}.timer enable failed"
  systemctl --user start "${t}.service" 2>/dev/null || echo "  ⚠️  ${t}.service start failed"
done

# 4. 환경 변수 drop-in 확인 및 생성
echo "[4] check NODE_EXPORTER_TEXTFILE_DIR"
env_line=$(systemctl --user show l4-weekly.service | grep '^Environment=' || true)
echo "Environment: ${env_line}"

# 환경 변수가 없으면 drop-in 생성 (idempotent)
if ! echo "$env_line" | grep -q "NODE_EXPORTER_TEXTFILE_DIR="; then
  echo "  → Creating environment drop-in..."
  mkdir -p ~/.config/systemd/user/l4-weekly.service.d
  
  for s in "${TIMERS[@]}"; do
    mkdir -p ~/.config/systemd/user/${s}.service.d
    cat > ~/.config/systemd/user/${s}.service.d/env.conf <<EOF
[Service]
Environment="NODE_EXPORTER_TEXTFILE_DIR=${HOME}/.cache/node_exporter/textfile"
Environment="TZ=UTC"
EOF
  done
  
  systemctl --user daemon-reload
  systemctl --user restart l4-weekly.service l4-daily.service 2>/dev/null || true
  echo "  ✅ drop-in written"
fi

# 5. 텍스트파일 디렉터리 생성 및 권한 보장
echo "[5] ensure textfile directory"
TEXTFILE_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
mkdir -p "${TEXTFILE_DIR}"
chmod 0755 "${TEXTFILE_DIR}" 2>/dev/null || true
# 소유자 변경 시도 (권한 있으면)
chown "$(whoami):$(whoami)" "${TEXTFILE_DIR}" 2>/dev/null || true

# 6. canonicalize (정렬·중복 제거)
echo "[6] canonicalize"
if [[ -x "$CANON" ]]; then
  bash "$CANON" || echo "  ⚠️  canonicalize had non-fatal error"
else
  echo "  ⚠️  canonicalize script not found/executable: $CANON"
fi

# 7. 그림자 재생 (데이터 공백 메우기)
echo "[7] shadow replay"
systemctl --user start "${SHADOW_UNIT}" 2>/dev/null || echo "  ⚠️  shadow replay start failed"
sleep 2

# 8. 검증 실행
echo "[8] validation"
if [[ -x "$VALID" ]]; then
  if bash "$VALID" >/tmp/l4_validation.boot.log 2>&1; then
    echo "  ✅ Validation passed"
    rm -f /var/run/l4_boot_validation_failed 2>/dev/null || true
  else
    echo "  ❌ Validation failed (see /tmp/l4_validation.boot.log)"
    touch /var/run/l4_boot_validation_failed 2>/dev/null || true
    logger -t l4-recover "L4 boot validation failed: see /tmp/l4_validation.boot.log" 2>/dev/null || true
    exit 2
  fi
else
  echo "  ⚠️  validation script missing"
fi

# 9. 부팅 상태 메트릭 생성
echo "[9] boot status metric"
if [[ -d "${TEXTFILE_DIR}" ]]; then
  if [[ -f /var/run/l4_boot_validation_failed ]]; then
    echo "l4_boot_status 1" > "${TEXTFILE_DIR}/l4_boot_status.prom"
  else
    echo "l4_boot_status 0" > "${TEXTFILE_DIR}/l4_boot_status.prom"
  fi
  chmod 0644 "${TEXTFILE_DIR}/l4_boot_status.prom" 2>/dev/null || true
  # Export timestamp
  bash "${WORK}/scripts/ops/inc/_export_timestamp.sh" "boot_status" || true
fi

# 11. 헬스 체크
echo "[11] health checks"
echo "  Timers:"
systemctl --user list-timers --all 2>/dev/null | grep -E 'l4-(daily|weekly|shadow|canonicalize)' || echo "    No timers found"

echo "  Latest decisions:"
if [[ -f "${WORK}/var/audit/decisions.ndjson" ]]; then
  jq -cr '. | {ts,decision,score}' "${WORK}/var/audit/decisions.ndjson" 2>/dev/null | tail -3 || echo "    No valid decisions found"
else
  echo "    decisions.ndjson not found"
fi

echo "  Prometheus directory: ${TEXTFILE_DIR}"
if [[ -d "${TEXTFILE_DIR}" ]]; then
  ls -lh "${TEXTFILE_DIR}"/l4_*.prom 2>/dev/null || echo "    No metric files found"
fi

echo ">>> L4 복구 완료: $(date) (log: $LOG)"

# 11. Generate selftest metric
echo "[12] generate selftest metric"
if [[ -f "${WORK}/scripts/ops/inc/l4_selftest_report.sh" ]]; then
  bash "${WORK}/scripts/ops/inc/l4_selftest_report.sh" || true
fi

# Save log for selftest report
cp "$LOG" /tmp/l4_recover.last.log 2>/dev/null || true

exit 0

