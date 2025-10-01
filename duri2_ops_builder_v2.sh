#!/usr/bin/env bash
# == DuRi2-OpsKit Mini Builder v2 ==
set -Eeuo pipefail

APP="duri2"
KIT_NAME="DuRi2-OpsKit"
STAMP="$(date +%Y%m%d_%H%M%S)"

# Desktop 추정
DESKTOP_CANDIDATES=("$HOME/Desktop" "/mnt/c/Users/admin/Desktop" "/mnt/c/Users/$USER/Desktop")
DESKTOP="$HOME"
for d in "${DESKTOP_CANDIDATES[@]}"; do [[ -d "$d" ]] && DESKTOP="$d" && break; done

KIT_DIR="$DESKTOP/$KIT_NAME"
PKG_DIR="$KIT_DIR/pkg-$STAMP"
mkdir -p "$PKG_DIR"/{scripts,config,systemd}

# Config
cat > "$PKG_DIR/config/duri2-ops.conf" <<'CONF'
APP_BASE="/opt/duri2"
LOG_DIR="/var/log/duri2-restore"
LOCK_DIR="/run/lock"
# 환경별 백업 소스 루트
BACKUP_ROOTS="/mnt/usb /mnt/c/Users/admin/Desktop/두리백업"
CONF

# Healthcheck
cat > "$PKG_DIR/scripts/duri2_healthcheck.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
CONFIG="${CONFIG:-/opt/duri2/config/duri2-ops.conf}"
[[ -f "$CONFIG" ]] && source "$CONFIG" || true
APP_BASE="${APP_BASE:-/opt/duri2}"
LOG_DIR="${LOG_DIR:-/var/log/duri2-restore}"
LOCK_DIR="${LOCK_DIR:-/run/lock}"
log(){ printf '[%(%F %T)T] %s\n' -1 "$*"; }
mkdir -p "$LOG_DIR" "$LOCK_DIR"

# restore (있으면)
if systemctl list-unit-files | grep -q '^duri2-restore.service'; then
  log "[STEP] restore start"
  systemctl start duri2-restore.service || true
  for i in {1..48}; do s="$(systemctl is-active duri2-restore.service || true)"; [[ "$s" == "inactive" || "$s" == "failed" ]] && break; sleep 10; done
else
  log "[WARN] restore.service not found"
fi

# watchdog (있으면)
if systemctl list-unit-files | grep -q '^duri2-watchdog.service'; then
  log "[STEP] watchdog start"
  systemctl start duri2-watchdog.service || true
else
  log "[WARN] watchdog.service not found"
fi

# 로그 요약
RUN_LOG="$(ls -1t ${LOG_DIR}/run_*.log 2>/dev/null | head -1 || true)"
[[ -n "$RUN_LOG" ]] && tail -n 30 "$RUN_LOG" || log "[WARN] no run_* log"
[[ -f "${LOG_DIR}/watchdog.log" ]] && tail -n 20 "${LOG_DIR}/watchdog.log" || log "[WARN] no watchdog.log"

ok=1
[[ -n "$RUN_LOG" ]] && grep -q 'RC=0' "$RUN_LOG" || ok=0
exit $(( ok ? 0 : 1 ))
SH
chmod +x "$PKG_DIR/scripts/duri2_healthcheck.sh"

# systemd (healthcheck + timer 09:10)
cat > "$PKG_DIR/systemd/duri2-healthcheck.service" <<'UNIT'
[Unit]
Description=DuRi2 OpsKit Healthcheck (restore+watchdog+logs)
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
User=root
Group=root
Environment=CONFIG=/opt/duri2/config/duri2-ops.conf
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/bin/bash -lc '/opt/duri2/scripts/duri2_healthcheck.sh'
PrivateTmp=true
ProtectSystem=full
ProtectHome=yes
ReadWritePaths=/var/log/duri2-restore /run/lock
UNIT

cat > "$PKG_DIR/systemd/duri2-healthcheck.timer" <<'UNIT'
[Unit]
Description=Daily DuRi2 OpsKit Healthcheck (09:10)

[Timer]
OnCalendar=*-*-* 09:10:00
Persistent=true
RandomizedDelaySec=0
Unit=duri2-healthcheck.service

[Install]
WantedBy=timers.target
UNIT

# install.sh (수정 ④ 디렉터리 보장 포함)
cat > "$PKG_DIR/install.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
APP_BASE="/opt/duri2"
LOG_DIR="/var/log/duri2-restore"
USR_NAME="duri"
USR_HOME="/home/duri"
USR_SCRIPTS="$USR_HOME/scripts"

echo "[STEP] layout"
sudo mkdir -p "$APP_BASE"/{scripts,config} "$LOG_DIR" "$USR_SCRIPTS"
sudo install -d -m 1777 /run/lock
sudo install -d -m 0755 "$LOG_DIR"
sudo chown -R "$USR_NAME:$USR_NAME" "$APP_BASE" "$LOG_DIR" "$USR_SCRIPTS"

# config (존재 시 보존)
[[ -f "$APP_BASE/config/duri2-ops.conf" ]] || { sudo cp -n ./config/duri2-ops.conf "$APP_BASE/config/"; sudo chown "$USR_NAME:$USR_NAME" "$APP_BASE/config/duri2-ops.conf"; }

# healthcheck 배치
sudo cp -f ./scripts/duri2_healthcheck.sh "$APP_BASE/scripts/"
sudo chmod +x "$APP_BASE/scripts/duri2_healthcheck.sh"

# watchdog SuccessExitStatus drop-in(있을 때만)
if systemctl list-unit-files | grep -q '^duri2-watchdog.service'; then
  sudo install -d -m 0755 /etc/systemd/system/duri2-watchdog.service.d
  printf "[Service]\nSuccessExitStatus=0 1 2\n" | sudo tee /etc/systemd/system/duri2-watchdog.service.d/policy.conf >/dev/null
fi

# systemd 등록
sudo cp -f ./systemd/duri2-healthcheck.service /etc/systemd/system/
sudo cp -f ./systemd/duri2-healthcheck.timer   /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now duri2-healthcheck.timer

# 편의 링크
sudo ln -sf "$APP_BASE/scripts/duri2_healthcheck.sh" "$USR_SCRIPTS/duri2_healthcheck.sh"

echo "[OK] OpsKit installed"
echo "▶ 수동 실행: sudo systemctl start duri2-healthcheck.service && journalctl -u duri2-healthcheck.service -n 50 --no-pager"
SH
chmod +x "$PKG_DIR/install.sh"

# uninstall.sh
cat > "$PKG_DIR/uninstall.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
APP_BASE="/opt/duri2"
USR_SCRIPTS="/home/duri/scripts"
systemctl disable --now duri2-healthcheck.timer 2>/dev/null || true
systemctl disable --now duri2-healthcheck.service 2>/dev/null || true
rm -f /etc/systemd/system/duri2-healthcheck.{service,timer}
systemctl daemon-reload || true
rm -f "$USR_SCRIPTS/duri2_healthcheck.sh"
rm -f "$APP_BASE/scripts/duri2_healthcheck.sh"
echo "[INFO] config/기존 restore·watchdog·로그는 보존"
echo "[OK] OpsKit uninstalled"
SH
chmod +x "$PKG_DIR/uninstall.sh"

# README (3-backticks 통일, 수정 ② 반영)
cat > "$PKG_DIR/README.md" <<'MD'
# DuRi2-OpsKit
restore/watchdog 연동 + healthcheck + systemd 타이머(일 1회 09:10)

## 설치
```bash
cd <압축해제한 폴더>
sudo bash install.sh
```

## 수동 실행/확인

```bash
sudo systemctl start duri2-healthcheck.service
journalctl -u duri2-healthcheck.service -n 100 --no-pager
systemctl list-timers | grep duri2-healthcheck
```

## 제거

```bash
sudo bash uninstall.sh
```
MD

# VERSION (수정 ①: 이스케이프 제거)
echo "version=$STAMP" > "$PKG_DIR/VERSION"

# 압축 생성 (수정 ① 반영)
mkdir -p "$KIT_DIR"
( cd "$(dirname "$PKG_DIR")" && tar -czf "${KIT_NAME}-${STAMP}.tar.gz" "$(basename "$PKG_DIR")" )

echo
echo "✅ 생성 완료"
echo "폴더: $PKG_DIR"
echo "패키지: $KIT_DIR/${KIT_NAME}-${STAMP}.tar.gz"
