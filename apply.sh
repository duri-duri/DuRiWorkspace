#!/usr/bin/env bash
set -Eeuo pipefail

# === 환경변수 ===
APPLY="${APPLY:-0}"                 # 0=DRY, 1=실행
USB="${USB:-/mnt/usb}"
HDD="${HDD:-/mnt/hdd}"
PLAN="${PLAN:?need PLAN.jsonl}"

CORE_OUT="$USB/CORE_PROTECTED"
FINAL_OUT="$USB/FINAL"
HDD_AR="$HDD/ARCHIVE"

# HDD가 마운트되어 있을 때만 디렉토리 생성
mkdir -p "$CORE_OUT/CORE" "$CORE_OUT/META" "$FINAL_OUT"
if [ -d "$HDD" ]; then
  mkdir -p "$HDD_AR/FULL" "$HDD_AR/CHECKPOINTS" "$HDD_AR/META"
  echo "[INFO] HDD 디렉토리 생성 완료: $HDD_AR"
else
  echo "[WARN] HDD 마운트되지 않음: $HDD (HDD 이관 건너뜀)"
fi

copy() {
  local src="$1" dst="$2"
  if [ "$APPLY" = "1" ]; then
    rsync -a --mkpath --info=NAME,PROGRESS2 "$src" "$dst"
  else
    echo "[DRY] $src  ->  $dst"
  fi
}

echo "== apply.sh :: APPLY=$APPLY =="
echo "[PLAN] $PLAN"

# 1) FULL 백업 파일들을 HDD로 이관 (USB에는 메타데이터만)
echo "[1/3] FULL 백업 파일 이관 계획:"
jq -r '.src' "$PLAN" | while read -r f; do
  [ -z "$f" ] && continue
  base="$(basename "$f")"
  echo "[DRY] FULL 백업: $base"
  [ -d "$HDD" ] && copy "$f" "$HDD_AR/FULL/$base" || echo "[SKIP] HDD 없음: $base"
done

# 2) SHA256SUMS 메타데이터 생성 및 USB 금고에 보존
echo "[2/3] SHA256SUMS 메타데이터 생성:"
jq -r 'select(.sha256 != null) | "\(.src)|\(.sha256)"' "$PLAN" | while IFS='|' read -r f hash; do
  [ -z "$f" ] && continue
  base="$(basename "$f")"
  meta_file="$CORE_OUT/META/SHA256SUMS.$(echo "$base" | sed 's/\.tar\.zst$//').txt"
  echo "$hash  $base" > "$meta_file"
  echo "[DRY] 메타데이터 생성: $meta_file"
  [ -d "$HDD" ] && copy "$meta_file" "$HDD_AR/META/$(basename "$meta_file")" || echo "[SKIP] HDD 없음: $meta_file"
done

# 3) GOLD FULL 메타(USB/FINAL) - 가장 최신 파일
echo "[3/3] GOLD FULL 메타데이터 생성:"
GOLD="$(jq -r '.src' "$PLAN" | sort | tail -1 || true)"
if [ -n "$GOLD" ]; then
  meta="$CORE_OUT/META/$(basename "$GOLD" .tar.zst).GOLD.txt"
  echo "GOLD_FULL=$(basename "$GOLD")" > "$meta"
  echo "SOURCE_PATH=$GOLD" >> "$meta"
  [ -d "$HDD" ] && echo "HDD_PATH=$HDD_AR/FULL/$(basename "$GOLD")" >> "$meta" || echo "HDD_PATH=NOT_AVAILABLE" >> "$meta"
  copy "$meta" "$FINAL_OUT/"
  echo "[DRY] GOLD 메타데이터: $meta"
fi

# 4) 금고 봉인(실행시에만)
if [ "$APPLY" = "1" ]; then
  chmod -R a-w "$CORE_OUT/CORE" || true
  fs="$(stat -f -c %T "$USB" 2>/dev/null || echo '?')"
  [[ "$fs" =~ ext4|ext2 ]] && sudo chattr +i "$CORE_OUT/CORE"/* 2>/dev/null || true
fi

echo "== DONE :: APPLY=$APPLY =="
