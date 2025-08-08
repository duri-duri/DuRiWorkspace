# Repository Cleanup Operation Checklist

## Pre-Execution Safety Checks

### [ ] Dependencies Verification
```bash
command -v jq sha256sum git git-filter-repo >/dev/null || exit 1
```

### [ ] Manifest Validation
```bash
jq -e '.must_exist' backups/CORE_BACKUPS.manifest.json >/dev/null || exit 1
```

### [ ] Safety Snapshot Creation
```bash
bash scripts/safety_snapshot.sh
```

## Execution Pipeline

### [ ] Step 1: Generate Deletion List
```bash
bash scripts/generate_delete_list.sh
```

### [ ] Step 2: Verify Deletion List
```bash
# Check that whitelist files are NOT in deletion list
jq -r '.must_exist[] | .path' backups/CORE_BACKUPS.manifest.json | while read file; do
    grep -q "^$file$" /tmp/to_delete.txt && echo "❌ ERROR: $file in deletion list" && exit 1
done
echo "✅ Whitelist files not in deletion list"
```

### [ ] Step 3: Execute Safe Filter
```bash
bash scripts/safe_filter_repo.sh
```

### [ ] Step 4: Post-Cleanup Verification
```bash
bash scripts/post_cleanup_report.sh
```

## GitHub Actions Setup

### [ ] Required Status Checks Configuration
1. Go to GitHub Settings → Branches
2. Add rule for `main` branch
3. Enable required status checks:
   - `must_exist_at_HEAD`
   - `archives_in_history_is_zero`
   - `objects_count_decreased`
4. Check "Include administrators"

### [ ] Actions Workflow Verification
```bash
# Verify workflow file exists
test -f .github/workflows/repo-guards.yml || echo "❌ Missing repo-guards.yml"
```

## Post-Merge Actions

### [ ] Repository Garbage Collection
```bash
git gc --prune=now --aggressive
```

### [ ] Tag Creation
```bash
git tag v1.0.0-cleanup
git push origin v1.0.0-cleanup
```

### [ ] Safety Backup Cleanup (Optional)
```bash
# Remove immutable protection
if [[ "$(uname)" == "Darwin" ]]; then
    chflags nouchg safety_backup/* 2>/dev/null || true
else
    chattr -i safety_backup/* 2>/dev/null || true
fi
# Remove safety backup
rm -rf safety_backup/
```

## Rollback Procedures

### [ ] Immediate Rollback (if issues detected)
```bash
git reset --hard refs/original/refs/heads/feat/duri-logging-autoinject
git push --force-with-lease origin HEAD:cleaned/main
```

### [ ] Safety Backup Restoration
```bash
# If core files were lost, restore from safety backup
cp safety_backup/* .
git add .
git commit -m "restore: core files from safety backup"
```

## Success Criteria

- [ ] Repository size reduced by >90%
- [ ] No archive files in Git history
- [ ] All must_exist files present in HEAD
- [ ] GitHub Actions checks pass
- [ ] PR merged successfully
- [ ] Tag created and pushed
