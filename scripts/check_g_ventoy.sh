#!/usr/bin/env bash
# G: Ventoy 드라이브 마운트 상태 확인 스크립트

echo "=== G: Ventoy 드라이브 마운트 확인 ==="
echo

# 1) /mnt/g가 실제 G: 드라이브를 가리키는지 확인
echo "1. /mnt/g 마운트 상태:"
if mountpoint -q /mnt/g 2>/dev/null; then
  mnt_dev=$(df -P /mnt/g 2>/dev/null | tail -1 | awk '{print $1}')
  if [ "$mnt_dev" = "/dev/sdb" ]; then
    echo "  [WARN] /mnt/g는 루트 파일시스템(/dev/sdb)을 가리킴 - G: 드라이브 미마운트"
  else
    echo "  [OK] /mnt/g는 마운트포인트 ($mnt_dev)"
  fi
else
  echo "  [WARN] /mnt/g는 마운트포인트가 아님"
fi

# 2) 스크린샷에 나온 실제 G: 드라이브 파일 확인
echo
echo "2. G: 드라이브 실제 내용 확인 (스크린샷 기준):"
found_items=0
[ -d /mnt/g/DuRiSync ] && { echo "  [OK] DuRiSync 폴더 존재"; found_items=$((found_items+1)); } || echo "  [NOT FOUND] DuRiSync"
[ -d /mnt/g/.logs ] && { echo "  [OK] .logs 폴더 존재"; found_items=$((found_items+1)); } || echo "  [NOT FOUND] .logs"
[ -d /mnt/g/.trash ] && { echo "  [OK] .trash 폴더 존재"; found_items=$((found_items+1)); } || echo "  [NOT FOUND] .trash"
[ -d /mnt/g/두리백업 ] && { echo "  [OK] 두리백업 폴더 존재"; found_items=$((found_items+1)); } || echo "  [NOT FOUND] 두리백업"
[ -f /mnt/g/30일\ git.txt ] && { echo "  [OK] 30일 git.txt 존재"; found_items=$((found_items+1)); } || echo "  [NOT FOUND] 30일 git.txt"
[ -f /mnt/g/github-recovery-codes.txt ] && { echo "  [OK] github-recovery-codes.txt 존재"; found_items=$((found_items+1)); } || echo "  [NOT FOUND] github-recovery-codes.txt"

echo
if [ $found_items -ge 3 ]; then
  echo "  [OK] G: 드라이브가 올바르게 마운트되어 있음 ($found_items/6 항목 발견)"
elif [ $found_items -gt 0 ]; then
  echo "  [WARN] 일부 항목만 발견됨 ($found_items/6 항목) - G: 드라이브 마운트 불완전"
else
  echo "  [ERR] G: 드라이브가 마운트되지 않음 (0/6 항목)"
fi

# 3) 마운트 명령 안내
echo
echo "3. G: 드라이브 수동 마운트 방법:"
echo "   sudo mount -t drvfs G: /mnt/g"
echo
echo "   또는 WSL 재시작 (Windows PowerShell):"
echo "   wsl --shutdown"
