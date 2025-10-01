#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${1:-/mnt/h/ARCHIVE}"
OUT="backup_repository/axes/$(date '+%Y%m%d_%H%M%S')"
mkdir -p "$OUT"/{backup_engine,integrity_provenance,learning_system,quality_improvement,runtime_container,storage_topology,operations_incident,security_secrets,_unclassified}
MANIFEST="$OUT/manifest.csv"
echo "sha256,size,mtime_epoch,axis,relpath,tags,provenance,run_id,depends_on,success" > "$MANIFEST"

cd "$ROOT"

# 후보 수집(텍스트/스크립트/로그/정책 중심)
mapfile -t FILES < <(find . -type f \
  \( -name "*.sh" -o -name "*.log" -o -name "*.txt" -o -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "SHA256SUMS*" -o -name "manifest.sha256*" \) \
  -not -path "*/.TRASH/*" -not -path "*/.quarantine/*" -print | sort)

# 헤더 우선 규칙(AXIS/TAGS/PROVENANCE가 선행하면 강제 적용)
read_header_axis() {
  local f="$1"; head -n 20 "$f" 2>/dev/null | grep -E '^#\s*AXIS:' | sed -E 's/^#\s*AXIS:\s*//I' | head -n1 || true
}
read_header_tags() {
  local f="$1"; head -n 20 "$f" 2>/dev/null | grep -E '^#\s*TAGS:' | sed -E 's/^#\s*TAGS:\s*//I' | head -n1 || true
}
read_header_prov() {
  local f="$1"; head -n 20 "$f" 2>/dev/null | grep -E '^#\s*PROVENANCE:' | sed -E 's/^#\s*PROVENANCE:\s*//I' | head -n1 || true
}

classify_by_path() {
  local p="$1"
  if   [[ "$p" =~ (^|/)(FULL|INCR|EXTENDED|CORE|CORE_PROTECTED|BACKUP|Desktop_Snapshots|Desktop_Mirror)(/|$) \
       || "$p" =~ unwrap_.*\.sh$ || "$p" =~ stage1_.*\.sh$ || "$p" =~ complete_unwrap.*\.sh$ \
       || "$p" =~ (backup|snapshot).*\.sh$ ]]; then echo backup_engine
  elif [[ "$p" =~ (^|/)SHA256SUMS.* || "$p" =~ VERIFY_.*\.log$ || "$p" =~ manifest\.sha256(\.raw)?$ \
       || "$p" =~ _HARDLINKS\.txt$ || "$p" =~ _SYMLINKS\.txt$ ]]; then echo integrity_provenance
  elif [[ "$p" =~ (^|/)(DuRiCore|duri_brain|CHECKPOINTS|CAPSULES)(/|$) \
       || "$p" =~ (learn|train|curriculum|brain).*\.sh$ ]]; then echo learning_system
  elif [[ "$p" =~ (^|/)(SECURITY|tests|policy)(/|$) \
       || "$p" =~ (quality|improve|optimi[sz]e|eval|benchmark).*\.sh$ ]]; then echo quality_improvement
  elif [[ "$p" =~ (^|/)(docker|compose|containers?|images?|volumes?)(/|$) \
       || "$p" =~ /var/lib/docker || "$p" =~ (docker|compose).*\.ya?ml$ ]]; then echo runtime_container
  elif [[ "$p" =~ (^|/)mount_status_backup_.*(/|$) \
       || "$p" =~ (lsblk|mount|df)_snap.*\.txt$ ]]; then echo storage_topology
  elif [[ "$p" =~ (^|/)(Logs|QUARANTINE|\.QUAR_FAIL|\.TRASH)(/|$) \
       || "$p" =~ (incident|runbook|recovery|timeline).*\.sh$ ]]; then echo operations_incident
  elif [[ "$p" =~ (^|/)(SECURITY)(/|$) \
       || "$p" =~ (secret|token|credential|keypolicy).*\.md$ ]]; then echo security_secrets
  else echo _unclassified
  fi
}

mkdir -p "$OLDPWD/$OUT"
for f in "${FILES[@]}"; do
  rel="${f#./}"
  axis_hdr=$(read_header_axis "$rel" || true)
  tags_hdr=$(read_header_tags "$rel" || true)
  prov_hdr=$(read_header_prov "$rel" || true)

  axis=$( [[ -n "$axis_hdr" ]] && echo "$axis_hdr" || classify_by_path "$rel" )

  sha=$(sha256sum "$rel" | awk '{print $1}')
  size=$(stat -c%s "$rel")
  mt=$(stat -c%Y "$rel")
  tags="${tags_hdr:-}"
  prov="path:$rel#sha256:$sha"
  [[ -n "$prov_hdr" ]] && prov="$prov | $prov_hdr"

  mkdir -p "$OLDPWD/$OUT/$axis/$(dirname "$rel")"
  ln -s "../../$ROOT/$rel" "$OLDPWD/$OUT/$axis/$rel" 2>/dev/null || true

  echo "$sha,$size,$mt,$axis,$rel,$tags,$prov" >> "$OLDPWD/$MANIFEST"
done

# 통계
{
  echo "=== AXIS COUNTS ==="
  cut -d, -f4 "$MANIFEST" | tail -n +2 | sort | uniq -c | sort -nr
} > "$OUT/stats.txt"

echo "DONE -> $OUT"
