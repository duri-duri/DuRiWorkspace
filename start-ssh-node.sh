#!/usr/bin/env bash
set -euo pipefail

# 1) root 패스워드 (개발용 기본값, 운영 전환 시 꼭 비활성/키인증으로)
: "${ROOT_PASSWORD:=duri123}"
echo "root:${ROOT_PASSWORD}" | chpasswd

# 2) sshd 설정 보증
mkdir -p /var/run/sshd
if ! grep -q "^PermitRootLogin" /etc/ssh/sshd_config 2>/dev/null; then
  echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
fi
if ! grep -q "^PasswordAuthentication" /etc/ssh/sshd_config 2>/dev/null; then
  echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
fi

# 3) 호스트키 없으면 생성
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
  ssh-keygen -A -f /
fi

# 4) sshd 백그라운드
/usr/sbin/sshd -D &
SSHD_PID=$!

# 5) SSH 서버 시작 대기
sleep 2

# 6) 원래 앱 실행
exec "$@"
