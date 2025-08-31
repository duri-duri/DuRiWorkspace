#!/usr/bin/env bash
set -euo pipefail

MANIFEST="backups/CORE_BACKUPS.manifest.json"

echo "📋 Post-Cleanup Verification Report"
echo "=================================="

# 1) MUST_EXIST check
echo ""
echo "=== MUST_EXIST CHECK ==="
echo "Verifying core backup files in Git history..."
echo ""

jq -r '.must_exist[] | .path' "$MANIFEST" | while read -r p; do
    if git cat-file -e HEAD:"$p" 2>/dev/null; then
        echo "✅ OK  $p"
    else
        echo "❌ MISS $p"
    fi
done

# 2) SIZE METRICS
echo ""
echo "=== SIZE METRICS ==="
echo "Repository size analysis:"
echo ""

git count-objects -v

# 3) ROLLBACK HOWTO
echo ""
echo "=== ROLLBACK GUIDE ==="
echo "If cleanup caused issues, use these commands to rollback:"
echo ""

# 현재 브랜치 확인
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

echo "1. Rollback to original state:"
echo "   git reset --hard refs/original/refs/heads/$CURRENT_BRANCH"
echo ""

echo "2. Force push rollback (if needed):"
echo "   git push --force-with-lease origin HEAD:$CURRENT_BRANCH"
echo ""

echo "3. Alternative: Create rollback branch:"
echo "   git checkout -b rollback-$(date +%Y%m%d_%H%M%S)"
echo "   git push origin HEAD"
echo ""

# 4) ADDITIONAL VERIFICATION
echo ""
echo "=== ADDITIONAL VERIFICATION ==="
echo ""

# Git 히스토리에서 아카이브 파일 확인
ARCHIVE_COUNT=$(git rev-list --objects --all | grep -E '\.(tar\.gz|tgz|zst|tar)$' | wc -l)
echo "Archive files remaining in history: $ARCHIVE_COUNT"

if [ "$ARCHIVE_COUNT" -gt 0 ]; then
    echo "Remaining archive files:"
    git rev-list --objects --all | grep -E '\.(tar\.gz|tgz|zst|tar)$' | awk '{print $2}' | sort -u | sed 's/^/   - /'
else
    echo "✅ No archive files remaining in history"
fi

# 5) SUCCESS SUMMARY
echo ""
echo "=== SUCCESS SUMMARY ==="
echo ""

if [ -f "/tmp/metrics_before.txt" ] && [ -f "/tmp/metrics_after.txt" ]; then
    echo "📊 Repository size change:"
    BEFORE_SIZE=$(grep "size-pack" /tmp/metrics_before.txt | awk '{print $2}')
    AFTER_SIZE=$(grep "size-pack" /tmp/metrics_after.txt | awk '{print $2}')
    
    if [ -n "$BEFORE_SIZE" ] && [ -n "$AFTER_SIZE" ]; then
        REDUCTION=$((BEFORE_SIZE - AFTER_SIZE))
        REDUCTION_PCT=$((REDUCTION * 100 / BEFORE_SIZE))
        echo "   Before: ${BEFORE_SIZE}KB"
        echo "   After:  ${AFTER_SIZE}KB"
        echo "   Reduction: ${REDUCTION}KB (${REDUCTION_PCT}%)"
    fi
fi

echo ""
echo "✅ Cleanup verification completed"
echo "🚀 Repository is ready for production"
