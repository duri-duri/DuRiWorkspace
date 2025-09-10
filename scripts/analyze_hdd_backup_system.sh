#!/bin/bash
# HDD 4TB 백업 시스템 전체 분석 스크립트

echo "🔍 HDD 4TB 백업 시스템 전체 분석"
echo "=================================="

# HDD 기본 정보
echo "📊 HDD 기본 정보:"
df -h /mnt/h

echo ""
echo "📁 ARCHIVE 디렉토리 구조 분석:"
echo "총 디렉토리 수: $(find /mnt/h/ARCHIVE -maxdepth 1 -type d | wc -l)"

echo ""
echo "📂 주요 백업 디렉토리들:"
for dir in BACKUP CORE CHECKPOINTS CAPSULES CORE_PROTECTED Desktop_Mirror Current_Backups; do
    if [ -d "/mnt/h/ARCHIVE/$dir" ]; then
        size=$(du -sh "/mnt/h/ARCHIVE/$dir" 2>/dev/null | cut -f1)
        files=$(find "/mnt/h/ARCHIVE/$dir" -type f 2>/dev/null | wc -l)
        echo "  ✅ $dir: $size ($files files)"
    else
        echo "  ❌ $dir: 없음"
    fi
done

echo ""
echo "📋 백업 파일 유형 분석:"
echo "CORE 백업 파일들:"
ls -lh /mnt/h/ARCHIVE/CORE/*.tar.zst 2>/dev/null | head -5 || echo "  없음"

echo ""
echo "일반 백업 파일들:"
ls -lh /mnt/h/ARCHIVE/*.tar.gz 2>/dev/null | head -5 || echo "  없음"

echo ""
echo "📅 날짜별 백업 분석:"
echo "2025-08 백업들:"
ls -la /mnt/h/ARCHIVE/2025-08/ 2>/dev/null | head -5 || echo "  없음"

echo ""
echo "🔧 백업 시스템 상태:"
echo "CHECKPOINTS:"
ls -la /mnt/h/ARCHIVE/CHECKPOINTS/ 2>/dev/null | head -3 || echo "  없음"

echo ""
echo "CAPSULES:"
ls -la /mnt/h/ARCHIVE/CAPSULES/ 2>/dev/null | head -3 || echo "  없음"

echo ""
echo "🎯 백업 시스템 효율성 분석:"
total_size=$(du -sh /mnt/h/ARCHIVE 2>/dev/null | cut -f1)
echo "ARCHIVE 총 크기: $total_size"

echo ""
echo "📊 백업 파일 통계:"
total_files=$(find /mnt/h/ARCHIVE -type f 2>/dev/null | wc -l)
tar_files=$(find /mnt/h/ARCHIVE -name "*.tar.*" 2>/dev/null | wc -l)
zst_files=$(find /mnt/h/ARCHIVE -name "*.zst" 2>/dev/null | wc -l)

echo "  총 파일 수: $total_files"
echo "  TAR 파일: $tar_files"
echo "  ZST 파일: $zst_files"

echo ""
echo "🚨 문제점 및 개선사항:"
echo "1. 백업 파일들이 여러 디렉토리에 분산되어 있음"
echo "2. 일관성 있는 네이밍 규칙 필요"
echo "3. 백업 정책 및 보존 기간 명확화 필요"
echo "4. 자동화된 백업 스케줄링 필요"

echo ""
echo "✅ 백업 시스템 리팩토링 권장사항:"
echo "1. 통합된 백업 디렉토리 구조 설계"
echo "2. 표준화된 백업 파일 네이밍 규칙"
echo "3. 자동화된 백업 스케줄링 시스템"
echo "4. 백업 무결성 검증 시스템"
echo "5. 백업 정책 및 보존 기간 관리"

echo ""
echo "🎯 다음 단계:"
echo "1. 현재 백업 시스템의 비효율성 상세 분석"
echo "2. 통합 백업 시스템 설계"
echo "3. 백업 자동화 스크립트 개발"
echo "4. 백업 정책 및 보존 기간 설정"

echo ""
echo "✅ HDD 백업 시스템 분석 완료"
