#!/usr/bin/env bash
set -Eeuo pipefail

# === 설정 ===
ROOT="${ROOT:-/mnt/h/ARCHIVE}"                         # 전체 스캔 루트
OUT="${OUT:-$ROOT/.UNWRAP/STAGE1}"                    # 언팩 루트
TRASH="${TRASH:-$ROOT/.TRASH/STAGE1_$(date +%Y%m%d_%H%M%S)}"  # 격리
JOBS="${JOBS:-1}"                                     # 1=순차(화면 스트리밍), 2~ 병렬(권장: 1)
MAX="${MAX:-0}"                                       # 0=전체, n=앞에서 n개만
LIST="$OUT/_lists/archives_1G.txt"
LOG="$OUT/_logs/run_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$OUT/_lists" "$OUT/_logs" "$TRASH"

say(){ printf '%s\n' "$*" | tee -a "$LOG"; }
hr(){ printf '%*s\n' "${COLUMNS:-80}" '' | tr ' ' - | tee -a "$LOG"; }

# === 1) 1GB+ 압축 파일 인덱싱 (확장자: tar.zst, zst, tar.gz, tgz, tar, zip, 7z) ===
if [[ ! -s "$LIST" ]]; then
  say "[INDEX] scanning $ROOT (>=1G archives)…"
  find "$ROOT" -type f -size +1G \
    -regextype posix-extended \
    -iregex '.*\.(tar\.zst|zst|tar\.gz|tgz|tar|zip|7z)$' \
    -not -path "$ROOT/.UNWRAP/*" -not -path "$ROOT/.TRASH/*" \
    -print | sort > "$LIST"
fi

TOTAL=$(wc -l < "$LIST" | tr -d ' ')
[[ "$TOTAL" -eq 0 ]] && { say "[INDEX] 1GB+ 압축 파일 없음. 종료"; exit 0; }

# MAX 제한(미리보기용)
if (( MAX > 0 )); then
  TMP_LIST="$LIST.tmp.$$"
  head -n "$MAX" "$LIST" > "$TMP_LIST"
  LIST="$TMP_LIST"
  TOTAL=$(wc -l < "$LIST" | tr -d ' ')
fi

say "[INDEX] targets: $TOTAL file(s)"
hr

# === 유틸 ===
# 대상 파일을 확장자 제거한 디렉토리명으로 언팩
_unpack_one(){
  local F="$1"
  local base="$(basename "$F")"
  local dir="$(dirname "$F")"
  local name="$base"

  case "$base" in
    *.tar.zst) name="${base%.tar.zst}";;
    *.tar.gz)  name="${base%.tar.gz}";;
    *.tgz)     name="${base%.tgz}";;
    *.zst)     name="${base%.zst}";;
    *.tar)     name="${base%.tar}";;
    *.zip)     name="${base%.zip}";;
    *.7z)      name="${base%.7z}";;
  esac

  local DST="$OUT/$name"
  local TMP="$DST.tmp.$$"
  mkdir -p "$TMP"

  # 포맷별 언팩
  if   [[ "$base" =~ \.tar\.zst$ ]]; then tar -I zstd -xf "$F" -C "$TMP"
  elif [[ "$base" =~ \.(tar\.gz|tgz)$ ]]; then tar -xzf "$F" -C "$TMP"
  elif [[ "$base" =~ \.tar$ ]]; then tar -xf "$F" -C "$TMP"
  elif [[ "$base" =~ \.zip$ ]]; then 7z x -y -o"$TMP" "$F" >/dev/null
  elif [[ "$base" =~ \.7z$ ]]; then  7z x -y -o"$TMP" "$F" >/dev/null
  elif [[ "$base" =~ \.zst$ ]]; then
    # 단순 .zst 단독 파일인 경우: 원본 파일 복원 시도 (tar 아님)
    unzstd -c "$F" > "$TMP/${base%.zst}" || { rm -rf "$TMP"; return 2; }
  else
    rm -rf "$TMP"; return 2
  fi

  # 완료 반영
  if [[ -e "$DST" ]]; then rm -rf "$DST"; fi
  mv "$TMP" "$DST"
  printf '%s' "$DST"
}

# 내부 압축백업(파일 바이트 기준) 중복 제거: 같은 해시 → 1개 보존, 나머지는 TRASH로
_dedupe_inner_archives(){
  local ROOTDIR="$1"
  local LIST_INNER
  mapfile -t LIST_INNER < <(find "$ROOTDIR" -type f -regextype posix-extended -iregex '.*\.(tar\.zst|zst|tar\.gz|tgz|tar|zip|7z)$' | sort)
  local N=${#LIST_INNER[@]}
  (( N == 0 )) && { say "[DEDUPE] no inner archives in $ROOTDIR"; return 0; }

  say "[DEDUPE] inner archives found: $N (hashing…)"
  # (경로 \t 바이트해시 \t 크기 \t mtime)
  local TMPMAP="$OUT/_logs/_inner.$$.tsv"
  : > "$TMPMAP"
  for f in "${LIST_INNER[@]}"; do
    # sha256 (파일 바이트 기준)
    h=$(sha256sum "$f" | awk '{print $1}')
    sz=$(stat -c %s "$f" 2>/dev/null || echo 0)
    mt=$(stat -c %Y "$f" 2>/dev/null || echo 0)
    printf "%s\t%s\t%s\t%s\n" "$f" "$h" "$sz" "$mt" >> "$TMPMAP"
  done

  # 같은 해시 그룹핑 → 보존정책: mtime 최신 우선, 같으면 size 큰 것
  # 동일 그룹에서 1개만 KEEP, 나머지는 TRASH로 이동
  awk -F'\t' '
    { path=$1; h=$2; sz=$3; mt=$4;
      key=h;
      if (!(key in best) || mt>best_mt[key] || (mt==best_mt[key] && sz>best_sz[key])) {
        best[key]=path; best_mt[key]=mt; best_sz[key]=sz;
      }
      paths[key]=paths[key] ? paths[key] RS path : path;
    }
    END {
      for (k in paths) {
        split(paths[k], arr, RS);
        keep=best[k];
        dupcnt=0; savesz=0;
        for (i in arr) {
          p=arr[i]; if (p=="") continue;
          if (p!=keep) {
            printf("[TRASH] %-s (dup of %s)\n", p, keep);
            printf("TRASH\t%s\t%s\n", p, k) > "/dev/stderr";
          }
        }
        printf("[KEEP ] %s\n", keep);
      }
    }' "$TMPMAP" 2> >(while read -r l; do echo "$l"; done | tee -a "$LOG") | tee -a "$LOG" | sed -n '1,200p'

  # 진짜 TRASH 이동(위 awk가 stderr로 "TRASH\t<path>\t<hash>"를 남김)
  while IFS=$'\t' read -r tag path hash; do
    [[ "$tag" != "TRASH" ]] && continue
    rel="${path#/}" ; tdir="$TRASH/inner_archives/$(dirname "$rel")"
    mkdir -p "$tdir"
    mv "$path" "$tdir/" || true
  done < <(awk -F'\t' '{print}' "$TMPMAP" | grep -E '^TRASH	')

  rm -f "$TMPMAP"
}

# === 2) 순차 처리(파일별 즉시 출력) ===
idx=0
while IFS= read -r F; do
  idx=$((idx+1))
  SIZEDISP=$(du -h "$F" | awk '{print $1}')
  say ""
  hr
  say "[${idx}/${TOTAL}] ⏱ START  $F  (size=$SIZEDISP)"
  START_EPOCH=$(date +%s)

  # 언팩
  set +e
  DST=$(_unpack_one "$F")
  rc=$?
  set -e
  if (( rc != 0 )); then
    say "[ERROR] unpack failed (rc=$rc) → skip: $F"
    continue
  fi
  say "[UNPACK] -> $DST"

  # 내부 중복 압축백업 정리
  _dedupe_inner_archives "$DST"

  END_EPOCH=$(date +%s)
  ELAPSED=$((END_EPOCH-START_EPOCH))
  say "[DONE ] $F  (${ELAPSED}s)"
  hr
done < "$LIST"

say ""
say "[SUMMARY] out: $OUT"
say "[SUMMARY] trash: $TRASH"
