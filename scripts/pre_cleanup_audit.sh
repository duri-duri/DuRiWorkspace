#!/usr/bin/env bash
set -euo pipefail

# Configuration
MANIFEST="backups/CORE_BACKUPS.manifest.json"
CONFIRM_PHRASE="I UNDERSTAND THE RISK"
WORKDIR=$(pwd)

echo "🔍 Pre-cleanup Audit Starting..."
echo "=================================="

# Check if manifest exists
if [ ! -f "$MANIFEST" ]; then
    echo "❌ ERROR: Manifest file not found: $MANIFEST"
    exit 1
fi

echo "✅ Manifest file found: $MANIFEST"

# 1) Verify must_exist files (path + SHA256)
echo ""
echo "📋 Verifying must_exist files..."
echo "--------------------------------"

jq -r '.must_exist[] | .path' "$MANIFEST" | while read -r path; do
    if [ ! -f "$path" ]; then
        echo "❌ MISSING: $path"
        exit 1
    fi
    echo "✅ Found: $path"
done

# Check SHA256 hashes
echo ""
echo "🔐 Verifying SHA256 hashes..."
echo "-----------------------------"

jq -r '.must_exist[] | "\(.sha256)  \(.path)"' "$MANIFEST" | while read -r line; do
    sha256=$(echo "$line" | awk '{print $1}')
    path=$(echo "$line" | awk '{for(i=2;i<=NF;i++) printf "%s%s", $i, (i==NF?"":" ")}')
    
    if ! echo "$sha256  $path" | sha256sum -c --status; then
        echo "❌ SHA256 MISMATCH: $path"
        echo "   Expected: $sha256"
        echo "   Actual: $(sha256sum "$path" | cut -d' ' -f1)"
        exit 1
    fi
    echo "✅ SHA256 OK: $path"
done

# 2) Generate deletion candidates
echo ""
echo "🗑️  Analyzing deletion candidates..."
echo "----------------------------------"

# Get all tar.gz files in repo
git ls-files | grep -E '\.(tar\.gz|tgz|zst|tar)$' | sort > /tmp/all_archive_files.txt

# Get whitelist paths
jq -r '.must_exist[] | .path' "$MANIFEST" > /tmp/whitelist.txt

# Generate deletion candidates (files not in whitelist)
grep -v -F -f /tmp/whitelist.txt /tmp/all_archive_files.txt > /tmp/deletion_candidates.txt

# Count and show summary
TOTAL_CANDIDATES=$(wc -l < /tmp/deletion_candidates.txt)
TOTAL_SIZE=$(du -ch $(cat /tmp/deletion_candidates.txt) 2>/dev/null | tail -1 | cut -f1)

echo "📊 Deletion Summary:"
echo "   - Total candidates: $TOTAL_CANDIDATES files"
echo "   - Estimated size: $TOTAL_SIZE"
echo ""

# Show top 20 candidates
echo "📝 Top 20 deletion candidates:"
head -20 /tmp/deletion_candidates.txt | sed 's/^/   - /'
echo ""

if [ "$TOTAL_CANDIDATES" -gt 20 ]; then
    echo "... and $((TOTAL_CANDIDATES - 20)) more files"
    echo ""
fi

# 3) Strong confirmation
echo "⚠️  WARNING: This will permanently remove $TOTAL_CANDIDATES files from Git history"
echo "   Total size: $TOTAL_SIZE"
echo ""
echo "📋 Files to be preserved:"
jq -r '.must_exist[] | "   - \(.path) (\(.description))"' "$MANIFEST"
echo ""

read -p "Type exactly '$CONFIRM_PHRASE' to proceed: " user_input

if [ "$user_input" != "$CONFIRM_PHRASE" ]; then
    echo "❌ Confirmation failed. Aborting cleanup."
    exit 1
fi

echo ""
echo "✅ Pre-cleanup audit PASSED"
echo "🚀 Ready to proceed with cleanup"
echo ""
echo "Next steps:"
echo "1. cd ../DuRiWorkspace.quarantine.git"
echo "2. Run git filter-repo with deletion candidates"
echo "3. Push cleaned history to new branch"
