#!/usr/bin/env bash
# sudo 없이 Shadow 루프 종료 (사용자 단위 systemd)
set -euo pipefail

echo "🛑 sudo 없이 Shadow 루프 종료 (사용자 단위 systemd)"

# 1) 사용자 단위 유닛 정지
echo "1. 사용자 단위 유닛 정지..."
systemctl --user stop duri-rag-eval.service duri-rag-eval-tuned.service duri-pr-gate.service 2>/dev/null || true

# 2) 사용자 단위 유닛 비활성화
echo "2. 사용자 단위 유닛 비활성화..."
systemctl --user disable duri-rag-eval.service duri-rag-eval-tuned.service duri-pr-gate.service 2>/dev/null || true

# 3) 재부팅 후 자동 시작 설정 (선택)
echo "3. 재부팅 후 자동 시작 설정..."
loginctl enable-linger "$USER" 2>/dev/null || true

echo "✅ Shadow 루프 종료 완료 (sudo 없이)"
