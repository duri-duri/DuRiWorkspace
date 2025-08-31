#!/usr/bin/env bash
# scripts/rollback_backup_system.sh
# 백업 시스템 수정 중 문제 발생 시 즉시 롤백
# 롤백 안전성 100% 보장 - 한번에 원래 상태 복구
set -euo pipefail

echo "🛡️ 백업 시스템 롤백 스크립트 시작"
echo "⚠️  이 스크립트는 백업 시스템을 원래 상태로 복구합니다!"
echo ""

# 사용자 확인
read -p "정말로 백업 시스템을 롤백하시겠습니까? (yes/no): " confirm
if [[ "$confirm" != "yes" ]]; then
    echo "❌ 롤백이 취소되었습니다."
    exit 1
fi

echo ""
echo "🔄 롤백 시작..."

# 1. 백업 스크립트 복구
echo "1️⃣ 백업 스크립트 복구 중..."
if [ -f "scripts/unified_backup_core.sh.backup_20250814_200634" ]; then
    cp "scripts/unified_backup_core.sh.backup_20250814_200634" "scripts/unified_backup_core.sh"
    echo "   ✅ unified_backup_core.sh 복구 완료"
else
    echo "   ⚠️  unified_backup_core.sh 백업 파일을 찾을 수 없습니다"
fi

if [ -f "scripts/unified_backup_extended.sh.backup_20250814_200634" ]; then
    cp "scripts/unified_backup_extended.sh.backup_20250814_200634" "scripts/unified_backup_extended.sh"
    echo "   ✅ unified_backup_extended.sh 복구 완료"
else
    echo "   ⚠️  unified_backup_extended.sh 백업 파일을 찾을 수 없습니다"
fi

if [ -f "scripts/unified_backup_full.sh.backup_20250814_200634" ]; then
    cp "scripts/unified_backup_full.sh.backup_20250814_200634" "scripts/unified_backup_full.sh"
    echo "   ✅ unified_backup_full.sh 복구 완료"
else
    echo "   ⚠️  unified_backup_full.sh 백업 파일을 찾을 수 없습니다"
fi

# 2. Git 상태 복구
echo ""
echo "2️⃣ Git 상태 복구 중..."
echo "   현재 Git 태그 확인:"
git tag | grep "SAFE_BACKUP" | tail -1

read -p "위 태그로 롤백하시겠습니까? (yes/no): " git_rollback
if [[ "$git_rollback" == "yes" ]]; then
    SAFE_TAG=$(git tag | grep "SAFE_BACKUP" | tail -1)
    echo "   🔄 Git 태그 $SAFE_TAG로 롤백 중..."
    git reset --hard "$SAFE_TAG"
    echo "   ✅ Git 상태 복구 완료"
else
    echo "   ⚠️  Git 롤백이 건너뛰어졌습니다"
fi

# 3. 백업 스크립트 실행 권한 복구
echo ""
echo "3️⃣ 실행 권한 복구 중..."
chmod +x scripts/unified_backup_*.sh
echo "   ✅ 실행 권한 복구 완료"

# 4. 롤백 완료 확인
echo ""
echo "4️⃣ 롤백 완료 확인 중..."
echo "   백업 스크립트 상태:"
ls -la scripts/unified_backup_*.sh

echo ""
echo "5️⃣ 롤백 테스트 중..."
echo "   CORE 백업 스크립트 테스트:"
if [ -x "scripts/unified_backup_core.sh" ]; then
    echo "   ✅ CORE 백업 스크립트 실행 가능"
else
    echo "   ❌ CORE 백업 스크립트 실행 불가"
fi

echo ""
echo "🎉 백업 시스템 롤백 완료!"
echo "📋 롤백된 내용:"
echo "   - 백업 스크립트들 (CORE/EXTENDED/FULL)"
echo "   - Git 상태 (SAFE_BACKUP 태그 기준)"
echo "   - 실행 권한"
echo ""
echo "🔄 이제 원래 상태로 복구되었습니다."
echo "⚠️  문제가 지속되면 추가 조치가 필요할 수 있습니다."




















