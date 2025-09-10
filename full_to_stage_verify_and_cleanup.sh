#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob

# ===== 설정 =====
ROOT="/mnt/h/ARCHIVE"                  # FULL_*.tar.* 가 있는 루트
TRASH="$ROOT/.TRASH"                   # 안전 이동 위치
DRYRUN=1                               # 1: 시뮬레이션, 0: 실제 이동
SAMPLE=16                              # 샘플 해시 대조 개수(0이면 목록만)
ZSTD_LONG=31                           # zstd long window

# STAGE 후보(순서대로 비교). 필요시 추가 가능
STAGE_DIRS=(
  "$ROOT/.UNWRAP/STAGE1"
  "$ROOT/.UNWRAP/STAGE2"
  "$ROOT/.UNWRAP/STAGE3"
  "$ROOT/.UNWRAP/extracted"            # extracted/<아카이브이름> 패턴도 지원
)

# ===== 유틸 =====
tar_list() {  # 아카이브 내 "파일" 목록(정규화)
  local arc="$1"
  case "$arc" in
    *.zst)  zstd -dc --long="$ZSTD_LONG" -- "$arc" | tar -tf - ;;
    *.gz|*.tgz) gzip -dc -- "$arc" | tar -tf - ;;
    *.tar)  tar -tf -- "$arc" ;;
    *)      return 2 ;;
  esac | sed 's#^\./##' | grep -v '/$'
}

tar_cat() {   # 아카이브에서 단일 파일 바이트 스트림
  local arc="$1" rel="$2"
  case "$arc" in
    *.zst)  zstd -dc --long="$ZSTD_LONG" -- "$arc" | tar -xO -f - -- "$rel" ;;
    *.gz|*.tgz) gzip -dc -- "$arc" | tar -xO -f - -- "$rel" ;;
    *.tar)  tar -xO -f "$arc" -- "$rel" ;;
  esac
}

stage_list_exact() {  # STAGE 안 파일목록(상대경로, 그대로)
  local dir="$1"
  (cd "$dir" && find . -type f -printf '%P\n')
}

stage_list_strip_top() {  # STAGE/최상위 폴더 한 겹 제거 후 목록
  local dir="$1"
  # 최상위 디렉토리가 하나뿐일 때 그 안으로 들어가 비교
  local first
  mapfile -t tops < <(find "$dir" -mindepth 1 -maxdepth 1 -type d -printf '%f\n')
  if (( ${#tops[@]} == 1 )); then
    (cd "$dir/${tops[0]}" && find . -type f -printf '%P\n')
  else
    return 3
  fi
}

move_to_trash() {
  local p="$1"
  mkdir -p -- "$TRASH"
  if (( DRYRUN )); then
    echo "[DRYRUN] → .TRASH 이동 예정: $p"
  else
    mv -vn -- "$p" "$TRASH/"
  fi
}

# ===== 메인: 루트의 FULL_*.tar.* 만 처리 =====
ok=0; skip=0; bytes=0

mapfile -t ARCS < <(find "$ROOT" -maxdepth 1 -type f \
  \( -name 'FULL_*.tar.zst' -o -name 'FULL_*.tar.gz' -o -name 'FULL_*.tgz' -o -name 'FULL_*.tar' \) \
  | LC_ALL=C sort)

if (( ${#ARCS[@]} == 0 )); then
  echo "처리할 FULL_*.tar.* 가 없습니다 (ROOT=$ROOT)."; exit 0
fi

for arc in "${ARCS[@]}"; do
  echo
  echo "[*] 대상: $arc"

  # 아카이브 이름에서 동명 폴더 후보(extracted/<base>)도 포함
  base=$(basename -- "$arc"); base="${base%.zst}"; base="${base%.gz}"; base="${base%.tgz}"; base="${base%.tar}"
  CANDS=()
  for s in "${STAGE_DIRS[@]}"; do
    [[ -d "$s" ]] || continue
    CANDS+=("$s")
    [[ -d "$s/$base" ]] && CANDS+=("$s/$base")
  done

  if (( ${#CANDS[@]} == 0 )); then
    echo "[-] STAGE 디렉터리를 찾지 못함 → 보류"
    ((skip++)); continue
  fi

  # 아카이브 목록 생성
  a=$(mktemp); trap 'rm -f "$a"' RETURN
  if ! tar_list "$arc" | LC_ALL=C sort -u > "$a"; then
    echo "[!] 아카이브 목록 읽기 실패 → 보류"
    ((skip++)); continue
  fi

  matched=""
  used_mode=""   # exact | strip-top

  # 각 STAGE 후보와 비교 (정확→한겹제거 순서)
  for dest in "${CANDS[@]}"; do
    [[ -d "$dest" ]] || continue

    b=$(mktemp)
    stage_list_exact "$dest" | LC_ALL=C sort -u > "$b" || true
    if diff -q "$a" "$b" >/dev/null 2>&1; then
      matched="$dest"; used_mode="exact"; rm -f "$b"; break
    fi
    # 한 겹 벗겨서 재시도
    stage_list_strip_top "$dest" 2>/dev/null | LC_ALL=C sort -u > "$b" || true
    if [[ -s "$b" ]] && diff -q "$a" "$b" >/dev/null 2>&1; then
      matched="$dest"; used_mode="strip-top"; rm -f "$b"; break
    fi
    rm -f "$b"
  done

  if [[ -z "$matched" ]]; then
    echo "[!] 파일 목록 불일치(어느 STAGE와도 매칭 안 됨) → 보류"
    ((skip++)); continue
  fi

  echo "    ↳ 매칭: $matched  (모드: $used_mode)"

  # 샘플 내용 해시 대조(옵션)
  if (( SAMPLE > 0 )); then
    mapfile -t samples < <(shuf -n "$SAMPLE" "$a" 2>/dev/null || head -n "$SAMPLE" "$a")
    for rel in "${samples[@]}"; do
      ah=$(tar_cat "$arc" "$rel" | sha256sum | awk '{print $1}') || { echo "[!] 아카이브 샘플 추출 실패: $rel"; matched=""; break; }
      # matched가 exact인지 strip-top인지에 따라 디스크 경로 계산
      case "$used_mode" in
        exact)  disk="$matched/$rel" ;;
        strip-top)
          # strip-top은 최상위 폴더명이 무엇이든 한 겹을 추가로 붙여본다
          top=$(find "$matched" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | head -n1)
          disk="$matched/$top/$rel"
          ;;
      esac
      bh=$(sha256sum -- "$disk" 2>/dev/null | awk '{print $1}') || { echo "[!] 디스크 샘플 없음: $disk"; matched=""; break; }
      [[ "$ah" == "$bh" ]] || { echo "[!] 샘플 해시 불일치: $rel"; matched=""; break; }
    done
    [[ -z "$matched" ]] && { echo "[!] 샘플 대조 실패 → 보류"; ((skip++)); continue; }
  fi

  size=$(stat -c '%s' -- "$arc" || echo 0)
  echo "[OK] 검증 통과 → 원본 아카이브 정리 대상"
  move_to_trash "$arc"
  ((ok++)); bytes=$((bytes + size))
done

echo
echo "==== 요약 ===="
echo "검증 통과(이동): $ok  |  보류: $skip"
printf '회수 가능 용량 합계: %.2f GB\n' "$(awk -v b="$bytes" 'BEGIN{printf b/1024/1024/1024}')"
echo "TRASH: $TRASH"
echo "DRYRUN=$DRYRUN  (실제 이동하려면 DRYRUN=0으로 변경)"




