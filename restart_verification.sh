#!/bin/bash
# 재시작 후 확인 스크립트
echo "=== 우측 자연어 명령창 + Ctrl+C 안정화 확인 ==="
echo

echo "1. 셸/커널 확인:"
echo "SHELL=$SHELL"
uname -a
which bash
echo

echo "2. 경로 접근 확인 (admin 사용):"
ls -la /mnt/c/Users/admin/Desktop | head -10
echo

echo "3. Ctrl+C 전달 테스트:"
echo "   다음 명령을 실행하고 Ctrl+C로 즉시 중단되는지 확인하세요:"
echo "   sleep 1000"
echo
echo "   ^C가 찍히고 프롬프트가 즉시 돌아오면 성공입니다!"
echo

echo "4. 터미널 설정 확인:"
echo "   terminal.integrated.sendKeybindingsToShell: true"
echo "   terminal.integrated.copyOnSelection: false"
echo

echo "=== 확인 완료 ==="
