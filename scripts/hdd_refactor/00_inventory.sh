#!/usr/bin/env bash
set -Eeuo pipefail
ROOTS=("/mnt/h/ARCHIVE" "/mnt/hdd/ARCHIVE")
META="/mnt/h/ARCHIVE/META"
LOG="/mnt/h/ARCHIVE/_logs/00_inventory_$(date +%F_%H%M).log"
OUT_ALL="$META/all_files.tsv"
OUT_SHA="$META/sha256_index.tsv"

mkdir -p "$META" "$(dirname "$LOG")"
: > "$LOG"

# (A) 파일 인벤토리: 항목별 즉시 append
: > "$OUT_ALL"
for R in "${ROOTS[@]}"; do
  find "$R" -path "$R/.TRASH" -prune -o -type f \
    -printf '%p\t%s\t%TY-%Tm-%Td %TH:%TM:%TS\n'
done | grep -vE '/META/|/_logs/|/state/|/reports/|/LEGACY$' \
   >> "$OUT_ALL"

# (B) sha256 인덱스: 1) *.sha256 2) META:SHA256SUMS 3) 미등록 직접해시
: > "$OUT_SHA"

# 1) *.sha256 재사용
for R in "${ROOTS[@]}"; do
  find "$R" -type f -name "*.sha256" | while read -r sf; do
    f="${sf%.sha256}"; [[ -f "$f" ]] || continue
    sha=$(awk '{print $1; exit}' "$sf" 2>/dev/null || true)
    [[ -n "${sha:-}" ]] || continue
    sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
    printf "%s\t%s\t%s\n" "$sha" "$sz" "$(realpath -m "$f")" >> "$OUT_SHA"
  done
done

# 2) META의 SHA256SUMS* 재사용
find "$META" -maxdepth 1 -type f -name "SHA256SUMS*" | while read -r sums; do
  while read -r sha fn; do
    [[ "$sha" =~ ^[0-9a-f]{64}$ ]] || continue
    base=$(basename "$fn"); f=""
    for R in "${ROOTS[@]}"; do
      f=$(find "$R" -type f -name "$base" | head -1 || true)
      [[ -n "$f" ]] && break
    done
    [[ -n "$f" ]] || continue
    sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
    grep -Fq "$(realpath -m "$f")" "$OUT_SHA" \
      || printf "%s\t%s\t%s\n" "$sha" "$sz" "$(realpath -m "$f")" >> "$OUT_SHA"
  done < "$sums"
done

# 3) 남은 아카이브 직접 해시(병렬)
TMP_ALL=$(mktemp)
for R in "${ROOTS[@]}"; do
  find "$R" -type f \( -name "*.tar.zst" -o -name "*.tar.gz" \)
done | sort -u > "$TMP_ALL"

comm -23 "$TMP_ALL" <(awk -F'\t' '{print $3}' "$OUT_SHA" | sort -u) \
| xargs -r -I{} -P4 bash -c '
  f="$1"; sha=$(sha256sum "$f" | awk "{print \$1}")
  sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
  printf "%s\t%s\t%s\n" "$sha" "$sz" "$(realpath -m "$f")"
' _ {} >> "$OUT_SHA"

echo "ALL=$(wc -l < "$OUT_ALL"), SHA=$(wc -l < "$OUT_SHA")" | tee -a "$LOG"
