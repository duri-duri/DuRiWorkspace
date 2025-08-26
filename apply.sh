#!/usr/bin/env bash
set -Eeuo pipefail

# =========================
# 옵션 파싱
# =========================
VERIFY_ONLY=0
KEEP_TMP=0
FULL_MANIFEST=0
QUIET=0
JSON_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --verify-only) VERIFY_ONLY=1 ;;
    --keep-tmp) KEEP_TMP=1 ;;
    --full-manifest) FULL_MANIFEST=1 ;;
    --quiet) QUIET=1 ;;
    --json-summary-only)
      JSON_ONLY=1
      QUIET=1
      ;;
  esac
done

# ---- logging helpers ----
log() { printf '%s\n' "$*" 1>&2; }          # 항상 stderr
say() { [ "${QUIET:-0}" -eq 0 ] && log "$@"; }  # QUIET이면 침묵

# JSON_ONLY: 모든 stdout을 stderr로 우회, 마지막에 fd3(원래 stdout)로 JSON만 1줄
if [ "$JSON_ONLY" -eq 1 ]; then
  exec 3>&1
  exec 1>&2
fi

# =========================
# PLAN 유틸리티
# =========================
# PLAN 항목 → "경로 문자열"로 정규화 (객체/문자열 모두 지원)
plan_paths() {
  jq -r '
    if type=="array" then .[] else . end
    | if type=="object" then (.src // .dst // .path // .)
      elif type=="string" then .
      else empty end
  ' "$PLAN"
}

# =========================
# 환경변수
# =========================
APPLY="${APPLY:-0}"                 # 0=DRY, 1=실행
USB="${USB:-/mnt/usb}"
HDD="${HDD:-/mnt/hdd}"
PLAN="${PLAN:?need PLAN.jsonl}"

CORE_OUT="$USB/CORE_PROTECTED"
FINAL_OUT="$USB/FINAL"
HDD_AR="$HDD/ARCHIVE"
META_DIR="${META_DIR:-$CORE_OUT/META}"

# =========================
# PLAN 사전 가드레일 (경고로 완화)
# =========================
if jq -r '
  if type=="array" then .[] else . end
  | if type=="object" then (.src // .dst // .path // .)
    elif type=="string" then .
    else empty end
' "$PLAN" | grep -E -v '^/mnt/hdd/ARCHIVE/(FULL|INCR)/' | grep . >/dev/null 2>&1; then
  [[ $QUIET -eq 0 ]] && log "[WARN] Some paths in plan don't follow /mnt/hdd/ARCHIVE/(FULL|INCR)/ pattern"
fi

# =========================
# 정확 매칭 해시 검증 함수
# =========================
check_one_exact() {
  local f="$1" base stem meta line hfile hmeta
  base="$(basename "$f")"
  stem="${base%.tar.zst}"
  meta="$META_DIR/SHA256SUMS.${stem}.txt"

  if [[ -f "$meta" ]]; then
    line="$(grep -F -- "  $base" "$meta" | head -1)"
    [[ -z "$line" ]] && { [[ $QUIET -eq 0 ]] && echo "[META-NOLINE] $base in $(basename "$meta")"; return 2; }
    hmeta="$(printf '%s\n' "$line" | tr -d '\r' | awk '{print $1}')"
  else
    meta="$(grep -RIl --include='SHA256SUMS.*' -e "  $base\$" "$META_DIR" | head -1 || true)"
    [[ -z "$meta" ]] && { [[ $QUIET -eq 0 ]] && echo "[NO META] $base"; return 2; }
    hmeta="$(grep -F -- "  $base" "$meta" | head -1 | tr -d '\r' | awk '{print $1}')"
  fi

  hfile="$(sha256sum -- "$f" | awk '{print $1}')"
  if [[ "$hfile" == "$hmeta" ]]; then
    [[ $QUIET -eq 0 ]] && echo "[OK] $base"
  else
    [[ $QUIET -eq 0 ]] && echo "[MISMATCH] $base (file=$hfile meta=$hmeta) [meta=$(basename "$meta")]"
    return 1
  fi
}

# =========================
# 디렉토리 준비
# =========================
mkdir -p "$META_DIR" "$FINAL_OUT"
if [[ $VERIFY_ONLY -eq 0 ]]; then
  mkdir -p "$CORE_OUT/CORE"
  if [ -d "$HDD" ]; then
    mkdir -p "$HDD_AR/FULL" "$HDD_AR/CHECKPOINTS" "$HDD_AR/META" "$HDD_AR/INCR"
    [[ $QUIET -eq 0 ]] && echo "[INFO] HDD 디렉토리 생성 완료: $HDD_AR"
  else
    [[ $QUIET -eq 0 ]] && echo "[WARN] HDD 마운트되지 않음: $HDD (HDD 이관 건너뜀)"
  fi
fi

# =========================
# 복사 래퍼
# =========================
copy() {
  local src="$1" dst="$2"
  if [ "$APPLY" = "1" ]; then
    mkdir -p "$(dirname "$dst")"
    if [ "$JSON_ONLY" -eq 1 ]; then
      rsync -a --info=NAME,PROGRESS2 -- "$src" "$dst" 1>&2
    else
      rsync -a --info=NAME,PROGRESS2 -- "$src" "$dst"
    fi
  else
    if [[ $VERIFY_ONLY -eq 1 ]]; then
      [[ $QUIET -eq 0 ]] && log "[VERIFY-SKIP] $src"
    else
      [[ $QUIET -eq 0 ]] && log "[DRY] $src -> $dst"
    fi
  fi
}

[[ $QUIET -eq 0 ]] && log "== apply.sh :: APPLY=$APPLY VERIFY_ONLY=$VERIFY_ONLY KEEP_TMP=$KEEP_TMP FULL_MANIFEST=$FULL_MANIFEST QUIET=$QUIET =="
[[ $QUIET -eq 0 ]] && log "[PLAN] $PLAN"

# =========================
# 메인 실행부
# =========================
if [[ $VERIFY_ONLY -eq 0 ]]; then
  [[ $QUIET -eq 0 ]] && log "== [APPLY MODE] 파일 이관 및 메타 생성 수행 =="

  # 1) 이관
  say "[1/3] 백업 파일 이관:"
  plan_paths | while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    base="$(basename "$f")"
    [[ $QUIET -eq 0 ]] && log "[COPY] $base"
    if [ -d "$HDD" ]; then
      subdir="$( [[ $base == FULL__* ]] && echo FULL || echo INCR )"
      copy "$f" "$HDD_AR/$subdir/$base"
    else
      [[ $QUIET -eq 0 ]] && log "[SKIP] HDD 없음: $base"
    fi
  done

  # 2) SHA256SUMS
  say "[2/3] SHA256SUMS 메타데이터 생성:"
  jq -r '
    if type=="array" then .[] else . end
    | if type=="object" and (.sha256 != null) then "\(.src // .dst // .path // .)|\(.sha256)"
      else empty end
  ' "$PLAN" \
  | while IFS='|' read -r f hash; do
      [[ -z "$f" ]] && continue
      base="$(basename "$f")"
      meta_file="$META_DIR/SHA256SUMS.${base%.tar.zst}.txt"
      printf "%s  %s\n" "$hash" "$base" > "$meta_file"
      [[ $QUIET -eq 0 ]] && log "[META] 생성: $meta_file"
      [ -d "$HDD" ] && copy "$meta_file" "$HDD_AR/META/$(basename "$meta_file")"
    done

  # 3) GOLD
  say "[3/3] GOLD FULL 메타데이터 생성:"
  GOLD="$(ls -1t "$HDD_AR/FULL"/FULL__*.tar.zst 2>/dev/null | head -1 || true)"
  if [[ -n "$GOLD" ]]; then
    base="$(basename "$GOLD")"
    src_from_plan="$(jq -r --arg b "$base" '
      if type=="array" then .[] else . end
      | if type=="object" and ((.src // .dst // .path // .) | endswith($b)) then (.src // .dst // .path // .)
        else empty end
    ' "$PLAN" | head -1 || true)"
    meta="$META_DIR/${base%.tar.zst}.GOLD.txt"
    {
      echo "GOLD_FULL=$base"
      echo "SOURCE_PATH=${src_from_plan:-UNKNOWN}"
      echo "HDD_PATH=$HDD_AR/FULL/$base"
    } > "$meta"
    copy "$meta" "$FINAL_OUT/"
    [[ $QUIET -eq 0 ]] && log "[GOLD] 최신 GOLD 지정: $base"
  fi

  # 4) 봉인
  if [ "$APPLY" = "1" ]; then
    chmod -R a-w "$CORE_OUT/CORE" 2>/dev/null || true
    fs="$(stat -f -c %T "$USB" 2>/dev/null || echo '?')"
    [[ "$fs" =~ ext4|ext2 ]] && sudo chattr +i "$CORE_OUT/CORE"/* 2>/dev/null || true
  fi
fi

# =========================
# 검증 & 요약
# =========================
[[ $QUIET -eq 0 ]] && log && log "====================" && log "[VERIFY & SUMMARY]" && log "===================="

tmpdir="$(mktemp -d)"
[[ $KEEP_TMP -eq 0 ]] && trap 'rm -rf "$tmpdir"' EXIT

jq -r '
  if type=="array" then .[] else . end
  | if type=="object" then (.src // .dst // .path // .)
    elif type=="string" then .
    else empty end
  | select(test("/FULL__"))
  | capture("(?<base>FULL__.*)").base
' "$PLAN" | sort -u > "$tmpdir/full.list" || true

jq -r '
  if type=="array" then .[] else . end
  | if type=="object" then (.src // .dst // .path // .)
    elif type=="string" then .
    else empty end
  | select(test("/INCR__"))
  | capture("(?<base>INCR__.*)").base
' "$PLAN" | sort -u > "$tmpdir/incr.list" || true

FULL_DIR="$HDD_AR/FULL"
INCR_DIR="$HDD_AR/INCR"

ok_full=0; bad_full_cnt=0
while IFS= read -r base; do
  f="$FULL_DIR/$base"
  [[ -f "$f" ]] || { [[ $QUIET -eq 0 ]] && echo "[MISS-FULL] $base"; continue; }
  if check_one_exact "$f" >/dev/null; then ((ok_full++)); else ((bad_full_cnt++)); fi
done < "$tmpdir/full.list"

ok_incr=0; bad_incr_cnt=0
while IFS= read -r base; do
  f="$INCR_DIR/$base"
  [[ -f "$f" ]] || { [[ $QUIET -eq 0 ]] && echo "[MISS-INCR] $base"; continue; }
  if check_one_exact "$f" >/dev/null; then ((ok_incr++)); else ((bad_incr_cnt++)); fi
done < "$tmpdir/incr.list"

if [[ $FULL_MANIFEST -eq 1 && $QUIET -eq 0 ]]; then
  echo "— FULL 전수 결과"; while IFS= read -r f; do check_one_exact "$FULL_DIR/$f" || true; done < "$tmpdir/full.list"
  echo "— INCR 전수 결과"; while IFS= read -r f; do check_one_exact "$INCR_DIR/$f" || true; done < "$tmpdir/incr.list"
fi

[[ $QUIET -eq 0 ]] && log && log "====================" && log "SUMMARY" && log "===================="
printf "개수: FULL 기대=%d 실제=%d | INCR 기대=%d 실제=%d\n" "$(<"$tmpdir/full.list" wc -l)" "$(ls -1 "$FULL_DIR" 2>/dev/null | wc -l)" "$(<"$tmpdir/incr.list" wc -l)" "$(ls -1 "$INCR_DIR" 2>/dev/null | wc -l)"
printf "무결성: FULL OK=%d BAD=%d | INCR OK=%d BAD=%d\n" "$ok_full" "$bad_full_cnt" "$ok_incr" "$bad_incr_cnt"

if (( bad_full_cnt==0 && bad_incr_cnt==0 )); then
  say "[ALL GREEN] 무결성 이상 없음 ✅"
  rc=0
else
  say "[ATTENTION] 무결성 불일치 존재 ❗"
  rc=1
fi

# ==== JSON 출력 (JSON_ONLY 모드일 때만) ====
if [ "$JSON_ONLY" -eq 1 ]; then
  full_expected="$(<"$tmpdir/full.list" wc -l)"
  incr_expected="$(<"$tmpdir/incr.list" wc -l)"
  full_ok="$ok_full"
  full_bad="$bad_full_cnt"
  incr_ok="$ok_incr"
  incr_bad="$bad_incr_cnt"

  if [ "${VERIFY_ONLY:-0}" -eq 1 ]; then
    printf '{"full_expected":%d,"incr_expected":%d,"full_ok":%d,"full_bad":%d,"incr_ok":%d,"incr_bad":%d,"rc":%d}\n' \
      "$full_expected" "$incr_expected" "$full_ok" "$full_bad" "$incr_ok" "$incr_bad" "$rc" >&3
  else
    printf '{"phase":"apply","rc":%d}\n' "$rc" >&3
  fi
fi

exit "$rc"
