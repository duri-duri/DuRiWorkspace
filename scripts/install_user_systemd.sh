#!/usr/bin/env bash
# 사용자 단위 systemd 설치 (sudo 없이)
set -euo pipefail

echo "🔧 사용자 단위 systemd 설치 (sudo 없이)"

# 사용자 systemd 디렉토리 생성
mkdir -p ~/.config/systemd/user

# 서비스 파일 복사
cp systemd/duri-rag-eval.service ~/.config/systemd/user/
cp systemd/duri-pr-gate.service ~/.config/systemd/user/
cp systemd/duri-rag-eval-tuned.service ~/.config/systemd/user/
cp systemd/duri-metrics-day66.service ~/.config/systemd/user/
cp systemd/duri-hygiene.service ~/.config/systemd/user/

# 타이머 파일 복사
cp systemd/duri-metrics-day66.timer ~/.config/systemd/user/
cp systemd/duri-hygiene.timer ~/.config/systemd/user/

# 사용자 systemd 활성화
systemctl --user daemon-reload

echo "✅ 사용자 단위 systemd 설치 완료"
echo "사용법:"
echo "  systemctl --user enable --now duri-metrics-day66.timer"
echo "  systemctl --user enable --now duri-hygiene.timer"
echo "  systemctl --user status duri-metrics-day66.timer"
echo ""
echo "로그인 세션 밖에서도 실행하려면:"
echo "  loginctl enable-linger $USER"


