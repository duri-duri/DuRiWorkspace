#!/usr/bin/env bash
set -euo pipefail

MANIFEST="backups/CORE_BACKUPS.manifest.json"

echo "🔍 Generating exact deletion list..."
echo "=================================="

# Check if manifest exists
if [ ! -f "$MANIFEST" ]; then
    echo "❌ ERROR: Manifest file not found: $MANIFEST"
    exit 1
fi

echo "✅ Manifest file found: $MANIFEST"

# 1) 히스토리 전수에서 아카이브 후보 산출
echo ""
echo "📋 Scanning Git history for archive files..."
git rev-list --objects --all | awk '{print $2}' \
 | grep -E '\.(tar\.gz|tgz|zst|tar)$' | sort -u > /tmp/candidates.txt

CANDIDATES_COUNT=$(wc -l < /tmp/candidates.txt)
echo "✅ Found $CANDIDATES_COUNT archive files in Git history"

# 2) 화이트리스트(보존 목록) 추출
echo ""
echo "📋 Extracting whitelist from manifest..."
jq -r '.must_exist[] | .path' "$MANIFEST" > /tmp/whitelist.txt

WHITELIST_COUNT=$(wc -l < /tmp/whitelist.txt)
echo "✅ Whitelist contains $WHITELIST_COUNT files to preserve"

# 3) 실제 삭제 목록 = 후보 - 보존
echo ""
echo "🗑️  Generating deletion list..."
grep -v -F -f /tmp/whitelist.txt /tmp/candidates.txt > /tmp/to_delete.txt

DELETE_COUNT=$(wc -l < /tmp/to_delete.txt)
echo "✅ Deletion list contains $DELETE_COUNT files"

# 4) 요약 리포트
echo ""
echo "📊 Summary:"
echo "   - Total archive files in history: $CANDIDATES_COUNT"
echo "   - Files to preserve (whitelist): $WHITELIST_COUNT"
echo "   - Files to delete: $DELETE_COUNT"
echo ""

# 5) 삭제 대상 미리보기
if [ "$DELETE_COUNT" -gt 0 ]; then
    echo "📝 Top 20 deletion candidates:"
    head -20 /tmp/to_delete.txt | sed 's/^/   - /'

    if [ "$DELETE_COUNT" -gt 20 ]; then
        echo "... and $((DELETE_COUNT - 20)) more files"
    fi
else
    echo "🎉 No files to delete! All archive files are in whitelist."
fi

echo ""
echo "✅ Deletion list generated: /tmp/to_delete.txt"
echo "🚀 Ready for safe_filter_repo.sh"
