#!/bin/bash
set -Eeuo pipefail
# DuRi 백업 상태 확인 스크립트
# HDD 백업 시스템 상태 점검

echo "🔍 DuRi 백업 시스템 상태 점검"
echo "================================"

# HDD 마운트 상태 확인
echo "📁 HDD 마운트 상태:"
df -h | grep -E "(hdd|h)" | head -5

echo ""
echo "📂 백업 디렉토리 구조:"
echo "HDD ARCHIVE:"
ls -la /mnt/hdd/ARCHIVE/ 2>/dev/null || echo "❌ HDD ARCHIVE 접근 불가"

echo ""
echo "📊 백업 파일 현황:"
echo "FULL 백업:"
ls -lh /mnt/hdd/ARCHIVE/FULL/ 2>/dev/null || echo "❌ FULL 백업 없음"

echo ""
echo "INCR 백업:"
ls -lh /mnt/hdd/ARCHIVE/INCR/ 2>/dev/null || echo "❌ INCR 백업 없음"

echo ""
echo "📋 PLAN_INCR.jsonl 상태:"
if [ -f "PLAN_INCR.jsonl" ]; then
    echo "✅ PLAN_INCR.jsonl 존재"
    echo "📄 파일 내용:"
    cat PLAN_INCR.jsonl | head -10
else
    echo "❌ PLAN_INCR.jsonl 없음"
fi

echo ""
echo "💾 현재 작업 공간 백업:"
if [ -d "backups/current_backup" ]; then
    echo "✅ 현재 백업 존재"
    ls -la backups/current_backup/ | head -5
else
    echo "❌ 현재 백업 없음"
fi

echo ""
echo "🎯 백업 시스템 권장사항:"
echo "1. HDD 백업 경로: /mnt/hdd/ARCHIVE/"
echo "2. Windows 백업 스크립트: ops/windows_backup/duri_backup_automation.ps1"
echo "3. Linux 백업 스크립트: scripts/duri_backup.sh"
echo "4. 백업 상태 모니터링: 이 스크립트 실행"

echo ""
echo "✅ 백업 시스템 점검 완료"
