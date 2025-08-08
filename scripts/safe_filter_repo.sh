#!/usr/bin/env bash
set -euo pipefail

CONFIRM="I UNDERSTAND THE RISK"
MANIFEST="backups/CORE_BACKUPS.manifest.json"
TODEL="/tmp/to_delete.txt"

echo "🛡️  Safe Filter-Repo Pipeline"
echo "=============================="

# 0) origin URL 보존
ORIGIN_URL="$(git remote get-url origin 2>/dev/null || true)"
if [ -n "$ORIGIN_URL" ]; then
    echo "✅ Origin URL preserved: $ORIGIN_URL"
else
    echo "⚠️  No origin URL found"
fi

# 1) must_exist 경로 + (있으면) sha256 검증
echo ""
echo "🔍 Pre-cleanup verification..."
echo "-------------------------------"

while read -r p; do
    if git cat-file -e HEAD:"$p" 2>/dev/null; then
        echo "✅ Found in history: $p"
    else
        echo "❌ MISSING in history: $p"
        exit 1
    fi
done < <(jq -r '.must_exist[] | .path' "$MANIFEST")

# SHA256 검증 (있는 경우)
if jq -e '.must_exist[0].sha256' "$MANIFEST" >/dev/null 2>&1; then
    echo ""
    echo "🔐 SHA256 verification..."
    echo "------------------------"
    if jq -r '.must_exist[] | "\(.sha256)  \(.path)"' "$MANIFEST" | sha256sum -c --status; then
        echo "✅ SHA256 verification passed"
    else
        echo "❌ SHA256 verification failed"
        exit 1
    fi
fi

echo "✅ must_exist verified (path + optional sha256)"

# 2) 삭제 목록 존재성 확인
echo ""
echo "📋 Checking deletion list..."
if [ ! -f "$TODEL" ]; then
    echo "❌ Deletion list not found: $TODEL"
    echo "   Run generate_delete_list.sh first"
    exit 1
fi

DELETE_COUNT=$(wc -l < "$TODEL")
if [ "$DELETE_COUNT" -eq 0 ]; then
    echo "🎉 No files to delete!"
    echo "✅ Cleanup not needed"
    exit 0
fi

echo "🧾 Deleting $DELETE_COUNT paths (single pass)"

# 3) 사람 확인(강한 확인)
echo ""
echo "⚠️  WARNING: This will permanently remove $DELETE_COUNT files from Git history"
echo "   Files to be preserved:"
jq -r '.must_exist[] | "   - \(.path) (\(.description))"' "$MANIFEST"
echo ""
read -p "Type exactly '$CONFIRM' to proceed: " ans

if [ "$ans" != "$CONFIRM" ]; then
    echo "❌ Confirmation failed. Aborting cleanup."
    exit 1
fi

# 4) 전 메트릭
echo ""
echo "📊 Pre-cleanup metrics..."
git count-objects -v > /tmp/metrics_before.txt
cat /tmp/metrics_before.txt

# 5) 단일 패스 실행(글롭 금지, --force 금지 → refs/original 보존)
echo ""
echo "🚀 Running git filter-repo (single pass)..."
echo "   This may take a few minutes..."

git filter-repo --paths-from-file "$TODEL" --invert-paths

echo "✅ git filter-repo completed"

# 6) origin 복원
if [ -n "$ORIGIN_URL" ]; then
    echo ""
    echo "🔗 Restoring origin URL..."
    git remote add origin "$ORIGIN_URL" 2>/dev/null || git remote set-url origin "$ORIGIN_URL"
    echo "✅ Origin URL restored"
fi

# 7) 후 메트릭 + 보존 재검증
echo ""
echo "🔍 Post-cleanup verification..."
echo "-------------------------------"

# 보존 파일 재검증
while read -r p; do
    if git cat-file -e HEAD:"$p" 2>/dev/null; then
        echo "✅ Still present: $p"
    else
        echo "❌ LOST after cleanup: $p"
        exit 1
    fi
done < <(jq -r '.must_exist[] | .path' "$MANIFEST")

echo "✅ must_exist still present in history"

# 메트릭 비교
git count-objects -v > /tmp/metrics_after.txt
echo ""
echo "📊 Post-cleanup metrics:"
cat /tmp/metrics_after.txt

# 8) 최종 검증 (푸시 전)
echo ""
echo "🔍 Final verification before push..."
echo "-----------------------------------"

# 아카이브 파일 잔존 확인
if git rev-list --objects --all | grep -E '\.(tar\.gz|tgz|zst|tar)$' >/dev/null; then
    echo "❌ Archives remain in history"
    git rev-list --objects --all | grep -E '\.(tar\.gz|tgz|zst|tar)$' | head -5
    exit 55
else
    echo "✅ No archives in history"
fi

# 9) 안전 푸시(운영 브랜치 직접 덮지 말고 cleaned/main로)
echo ""
echo "🚀 Pushing to cleaned/main (safe with-lease)..."
CURRENT_HEAD="$(git rev-parse --abbrev-ref HEAD || echo HEAD)"
git push --force-with-lease origin HEAD:cleaned/main

echo ""
echo "✅ Successfully pushed to cleaned/main"
echo "📋 Next steps:"
echo "   1. Create PR: cleaned/main → main"
echo "   2. Review changes"
echo "   3. Merge after 24h observation"
echo "   4. Tag: v1.0.0-cleanup"
echo ""
echo "📄 Metrics comparison:"
diff -u /tmp/metrics_before.txt /tmp/metrics_after.txt || echo "   (No significant changes in metrics)"
