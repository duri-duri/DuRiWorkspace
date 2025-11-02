#!/usr/bin/env bash
# G: 드라이브 자동 마운트를 위한 sudoers 설정 스크립트
set -euo pipefail

echo "=== G: 드라이브 자동 마운트 sudoers 설정 ==="
echo ""

# 마운트 스크립트 경로 확인
MOUNT_SCRIPT="$HOME/DuRiWorkspace/scripts/_mount_g.sh"
UMOUNT_SCRIPT="$HOME/DuRiWorkspace/scripts/_umount_g.sh"

# sudoers 설정 내용 (스크립트 경로 사용)
SUDOERS_CONTENT="# DuRi G: 드라이브 자동 마운트 (비밀번호 없음)
# $(date '+%Y-%m-%d %H:%M:%S')
duri ALL=(ALL) NOPASSWD: $MOUNT_SCRIPT
duri ALL=(ALL) NOPASSWD: $UMOUNT_SCRIPT
"

# 임시 파일 생성
TMP_FILE=$(mktemp)
echo "$SUDOERS_CONTENT" > "$TMP_FILE"

echo "1. sudoers 설정 파일 생성:"
echo "$SUDOERS_CONTENT"
echo ""

echo "2. sudoers 문법 검사:"
if sudo visudo -cf "$TMP_FILE" 2>&1; then
  echo "   [OK] sudoers 문법 검사 통과"
else
  echo "   [ERR] sudoers 문법 오류"
  rm -f "$TMP_FILE"
  exit 1
fi

echo ""
echo "3. sudoers.d에 복사:"
if sudo cp "$TMP_FILE" /etc/sudoers.d/duri_g_mount; then
  echo "   [OK] 파일 복사 성공"
else
  echo "   [ERR] 파일 복사 실패"
  rm -f "$TMP_FILE"
  exit 1
fi

echo ""
echo "4. 권한 설정:"
if sudo chmod 0440 /etc/sudoers.d/duri_g_mount; then
  echo "   [OK] 권한 설정 완료 (0440)"
else
  echo "   [ERR] 권한 설정 실패"
  rm -f "$TMP_FILE"
  exit 1
fi

rm -f "$TMP_FILE"

echo ""
echo "5. 설정 확인:"
sudo cat /etc/sudoers.d/duri_g_mount

echo ""
echo "=== 설정 완료 ==="
echo ""
echo "이제 비밀번호 없이 G: 드라이브 마운트가 가능합니다:"
echo "  sudo $MOUNT_SCRIPT"
echo "  또는"
echo "  sudo ~/DuRiWorkspace/scripts/_mount_g.sh"
echo ""
echo "테스트 실행:"
echo "  sudo $UMOUNT_SCRIPT  # 언마운트"
echo "  sudo $MOUNT_SCRIPT   # 마운트 (비밀번호 없이)"
echo "  ls /mnt/g"

