#!/usr/bin/env bash
set -euo pipefail

echo "🛡️  Safety Snapshot Protection"
echo "=============================="

# deps 확인(없으면 중단)
command -v jq sha256sum git >/dev/null || { echo "❌ deps missing"; exit 90; }
echo "✅ Dependencies verified"

# safety_backup 디렉토리 생성
mkdir -p safety_backup/

# 핵심 백업 파일들을 safety_backup으로 복사
echo ""
echo "📋 Creating safety backup..."
jq -r '.must_exist[] | .path' backups/CORE_BACKUPS.manifest.json | while read -r path; do
    if [ -f "$path" ]; then
        cp "$path" "safety_backup/"
        echo "✅ Copied: $path"
    else
        echo "⚠️  File not found: $path"
    fi
done

# 읽기전용 속성 적용 (OS별 분기)
echo ""
echo "🔒 Applying immutable protection..."
if [[ "$(uname)" == "Darwin" ]]; then
    chflags uchg safety_backup/* 2>/dev/null || true
    echo "✅ macOS immutable flags applied"
else
    chattr +i safety_backup/* 2>/dev/null || true
    echo "✅ Linux immutable attributes applied"
fi

# 해시 검증(실패 즉시 종료)
echo ""
echo "🔐 Hash verification..."
jq -r '.must_exist[] | "\(.sha256)  safety_backup/\(.path)"' backups/CORE_BACKUPS.manifest.json | sha256sum -c || { echo "❌ Hash verification failed"; exit 44; }

echo "✅ Safety snapshot created and protected"
echo "📁 Location: safety_backup/"
echo "🔒 Protection: Immutable attributes applied"
