#!/usr/bin/env bash
set -Eeuo pipefail

# 안전 추출 + 전수 무결성 + 메타데이터 비교 + 2단계 안전삭제
# 최적화: GNU tar 사용 시 --to-command 로 1-pass에서 원본 바이트 해시 전수 계산
# fallback: GNU tar 미사용 시 다중 패스(안전하지만 느림)

ARC="${1:-}"; [[ -z "$ARC" ]] && { echo "사용법: $0 <아카이브>"; exit 1; }
[[ ! -f "$ARC" ]] && { echo "에러: 파일 없음 $ARC"; exit 1; }

# 목적지
DEST="${ARC%.tar.zst}"; DEST="${DEST%.tar.gz}"; DEST="${DEST%.tgz}"; DEST="${DEST%.tar}"
HASHDIR="${DEST}.arc_hashes"   # 원본(아카이브 스트림)에서 계산한 SHA256 저장소
FALLBACK="${FALLBACK:-auto}"   # auto | force | off   (auto: GNU tar만 최적화)
ZSTD_LONG="${ZSTD_LONG:-31}"   # zstd dictionary window

echo "=== 안전한 압축 해제 및 전수 검증 시작 (최적화 버전) ==="
echo "원본 파일: $ARC"
echo "추출 폴더: $DEST"
echo "해시 저장소: $HASHDIR"

# 1) 아카이브 무결성
echo "1) 원본 아카이브 무결성 검사..."
case "$ARC" in
  *.tar.zst) zstd -t --long="$ZSTD_LONG" -- "$ARC" ;;
  *.tar.gz|*.tgz) gzip -t -- "$ARC" ;;
  *.tar) tar -tf "$ARC" >/dev/null ;;
  *) echo "에러: 확장자 미지원"; exit 2;;
esac
echo "✅ 아카이브 무결성 통과"

# 2) 목록 수집(정렬, 엔트리 전부; 디렉토리/링크 포함)
echo "2) 아카이브 파일 목록 추출..."
ORIGINAL_LIST=$(mktemp)
case "$ARC" in
  *.tar.zst) zstd -dc --long="$ZSTD_LONG" -- "$ARC" | tar -tf - ;;
  *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar -tf - ;;
  *.tar) tar -tf "$ARC" ;;
esac | sed 's#^\./##' | LC_ALL=C sort > "$ORIGINAL_LIST"
ORIGINAL_COUNT=$(wc -l < "$ORIGINAL_LIST")
echo "   원본 엔트리 수: $ORIGINAL_COUNT"

# 3) 추출 (umask 영향 제거 + 권한 보존 시도)
echo "3) 추출..."
mkdir -p "$DEST"
OLDUMASK=$(umask)
umask 000   # umask가 권한을 깎지 않도록
# GNU tar면 --same-permissions(-p) 적용 (root가 아니어도 mode 보존에 도움)
case "$ARC" in
  *.tar.zst) zstd -dc --long="$ZSTD_LONG" -- "$ARC" | tar -xpf - -C "$DEST" ;;
  *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar -xpf - -C "$DEST" ;;
  *.tar) tar -xpf "$ARC" -C "$DEST" ;;
esac
umask "$OLDUMASK"
echo "✅ 추출 완료"

# 4) 추출 목록
echo "4) 추출 목록 생성..."
EXTRACTED_LIST=$(mktemp)
( cd "$DEST" && find . -mindepth 1 -printf '%P\n' | LC_ALL=C sort > "$EXTRACTED_LIST" )
EXTRACTED_COUNT=$(wc -l < "$EXTRACTED_LIST")
echo "   추출 엔트리 수: $EXTRACTED_COUNT"

# 5) 목록 비교
echo "5) 목록 비교..."
diff -u "$ORIGINAL_LIST" "$EXTRACTED_LIST" >/dev/null || {
  echo "❌ 목록 불일치"; diff -u "$ORIGINAL_LIST" "$EXTRACTED_LIST" | head -50; exit 3;
}
echo "✅ 목록 일치"

# 5b) 메타데이터 비교 (권한 차이 처리 포함)
echo "5b) tar 메타데이터 비교..."
META_DIFF_LOG=$(mktemp)
set +e
case "$ARC" in
  *.tar.zst) zstd -dc --long="$ZSTD_LONG" -- "$ARC" | tar --compare -f - -C "$DEST" 2>&1 | tee "$META_DIFF_LOG" ;;
  *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar --compare -f - -C "$DEST" 2>&1 | tee "$META_DIFF_LOG" ;;
  *.tar) tar --compare -f "$ARC" -C "$DEST" 2>&1 | tee "$META_DIFF_LOG" ;;
esac
RC_META=${PIPESTATUS[1]}
set -e

if [[ $RC_META -ne 0 ]]; then
  # 1) 모든 불일치가 "Mode differs" 뿐인지 확인
  if grep -qv "Mode differs" "$META_DIFF_LOG"; then
    echo "❌ 에러: 메타데이터 비교 실패(권한 외 차이 존재)"
    sed -n '1,50p' "$META_DIFF_LOG"
    rm -f "$META_DIFF_LOG" "$ORIGINAL_LIST" "$EXTRACTED_LIST"
    exit 6
  fi

  # 2) 대상 파일시스템이 권한 미지원/약한 경우는 경고로 강등
  FS_TYPE=$(stat -f -c %T "$DEST" 2>/dev/null || echo unknown)
  case "$FS_TYPE" in
    ntfs|fuseblk|exfat|vfat|msdos|fat)
      echo "⚠️ 경고: 파일시스템($FS_TYPE) 권한 매핑 한계로 'Mode differs' 무시(콘텐츠 해시는 전수 검증)."
      ;;
    *)
      # 엄격 모드이면 실패, 아니면 경고로 통과
      if [[ "${STRICT_META:-0}" -eq 1 ]]; then
        echo "❌ 에러: STRICT_META=1 이며 권한 차이 존재 → 실패"
        sed -n '1,50p' "$META_DIFF_LOG"
        rm -f "$META_DIFF_LOG" "$ORIGINAL_LIST" "$EXTRACTED_LIST"
        exit 6
      else
        echo "⚠️ 경고: POSIX FS($FS_TYPE)이지만 권한 차이만 존재 → 권고상 조정 필요. (콘텐츠 해시 전수 검증으로 커버)"
        sed -n '1,20p' "$META_DIFF_LOG"
      fi
      ;;
  esac
else
  echo "✅ 메타데이터 비교 통과"
fi
rm -f "$META_DIFF_LOG"

is_gnu_tar() { tar --version 2>/dev/null | grep -q 'GNU tar'; }

# 6) 전수 콘텐츠 해시 검증
# 최적: GNU tar → --to-command 로 regular file만 1-pass 해시
# 규칙: 디렉토리/링크 등은 메타데이터 비교로 충분, 해시는 "일반파일만"
echo "6) 전수 콘텐츠 해시 검증(일반파일)..."
mkdir -p "$HASHDIR"
cleanup_hashes() {
  # 빈 디렉터리 정리(선택)
  find "$HASHDIR" -type f -name '*.sha256' -size 0 -delete 2>/dev/null || true
}
trap cleanup_hashes EXIT

calc_hashes_onepass() {
  echo "   최적화 모드: GNU tar 1-pass 해시 계산..."
  # tar가 각 엔트리를 순회하며 regular file에 대해서만 해시 파일을 저장
  # GNU tar 변수: TAR_FILENAME, TAR_FILETYPE('0' 또는 'f'가 파일)
  case "$ARC" in
    *.tar.zst)
      zstd -dc --long="$ZSTD_LONG" -- "$ARC" | \
      tar --to-command='
        case "${TAR_FILETYPE:-?}" in
          f|0)
            out="'"$HASHDIR"'/${TAR_FILENAME}.sha256"
            mkdir -p "$(dirname "$out")"
            sha256sum | awk "{print \$1}" > "$out"
            ;;
        esac
      ' -xf - >/dev/null
      ;;
    *.tar.gz|*.tgz)
      gzip -dc -- "$ARC" | \
      tar --to-command='
        case "${TAR_FILETYPE:-?}" in
          f|0)
            out="'"$HASHDIR"'/${TAR_FILENAME}.sha256"
            mkdir -p "$(dirname "$out")"
            sha256sum | awk "{print \$1}" > "$out"
            ;;
        esac
      ' -xf - >/dev/null
      ;;
    *.tar)
      tar --to-command='
        case "${TAR_FILETYPE:-?}" in
          f|0)
            out="'"$HASHDIR"'/${TAR_FILENAME}.sha256"
            mkdir -p "$(dirname "$out")"
            sha256sum | awk "{print \$1}" > "$out"
            ;;
        esac
      ' -xf "$ARC" >/dev/null
      ;;
  esac
}

calc_hashes_fallback() {
  echo "   Fallback 모드: 다중 패스 해시 계산..."
  # 느리지만 확실: 각 파일을 아카이브에서 다시 읽어 해시(다중 패스)
  mapfile -t PATHS < <(grep -v '/$' "$ORIGINAL_LIST")  # 디렉토리 제외
  for p in "${PATHS[@]}"; do
    # p가 링크 등일 수도 있으므로 실제 regular file인지 확인
    ftype=$(
      case "$ARC" in
        *.tar.zst) zstd -dc --long="$ZSTD_LONG" -- "$ARC" | tar -tvf - | grep -F -- "$p" | awk 'NR==1{print substr($1,1,1)}' ;;
        *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar -tvf - | grep -F -- "$p" | awk 'NR==1{print substr($1,1,1)}' ;;
        *.tar) tar -tvf "$ARC" | grep -F -- "$p" | awk 'NR==1{print substr($1,1,1)}' ;;
      esac
    )
    [[ "$ftype" != "-" ]] && continue
    out="$HASHDIR/$p.sha256"; mkdir -p "$(dirname "$out")"
    h=$(
      case "$ARC" in
        *.tar.zst) zstd -dc --long="$ZSTD_LONG" -- "$ARC" | tar -xO -f - -- "$p" | sha256sum | awk '{print $1}' ;;
        *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar -xO -f - -- "$p" | sha256sum | awk '{print $1}' ;;
        *.tar) tar -xO -f "$ARC" -- "$p" | sha256sum | awk '{print $1}' ;;
      esac
    )
    printf '%s\n' "$h" > "$out"
  done
}

if { [[ "$FALLBACK" = auto ]] && is_gnu_tar; } || [[ "$FALLBACK" = off && is_gnu_tar ]]; then
  calc_hashes_onepass
else
  calc_hashes_fallback
fi

# 파일시스템 해시와 비교
echo "   해시 비교 중..."
FAILED=0
while IFS= read -r rel; do
  # regular file만 비교
  [[ -f "$DEST/$rel" ]] || continue
  [[ -L "$DEST/$rel" ]] && continue
  if [[ ! -f "$HASHDIR/$rel.sha256" ]]; then
    echo "❌ 원본해시 없음: $rel"; FAILED=1; continue
  fi
  ORG=$(cat "$HASHDIR/$rel.sha256")
  CUR=$(sha256sum -- "$DEST/$rel" | awk '{print $1}')
  if [[ "$ORG" != "$CUR" ]]; then
    echo "❌ 해시 불일치: $rel"
    echo "  원본: $ORG"
    echo "  추출: $CUR"
    FAILED=1
  fi
done < <(grep -v '/$' "$ORIGINAL_LIST")

[[ $FAILED -ne 0 ]] && { echo "❌ 전수 해시 검증 실패"; exit 4; }
echo "✅ 전수 해시 검증 통과"

# 7) 모든 검증 통과 → 2단계 안전 삭제
echo "7) 모든 검증 통과: 원본 안전 삭제 준비..."
TO_DELETE="${ARC}.to_delete"
mv -v -- "$ARC" "$TO_DELETE"
sync
rm -v -- "$TO_DELETE"
echo "✅ 원본 삭제 완료"

# 마무리
rm -f "$ORIGINAL_LIST" "$EXTRACTED_LIST"
echo "=== 모든 작업 완료 ==="
echo "추출 폴더: $DEST"





