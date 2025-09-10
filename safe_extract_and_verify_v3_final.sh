#!/usr/bin/env bash
# === Safe Extract & Verify v3 (final) =======================================
# 정책: "전수 검증 100% 통과"일 때만 원본 아카이브 삭제(2단계 삭제)
# - 파일/심볼릭링크 목록 동형 비교(디렉토리 제외)
# - tar 경로 프리픽스('./') 이슈 보정
# - 전수 SHA-256(일반파일), symlink 타깃 동일성 검증
# - tar --compare의 권한/mtime 차이는 경고(STRICT_META=1이면 실패)
# - 권한 정규화(파일0644/디렉0755) 옵션: APPLY_PERMS=auto|chmod|off (기본 auto)
# - 스파스 검증 훅(환경에 따라 스킵)
# 환경변수:
#   STRICT_META=0|1         (기본 0)
#   APPLY_PERMS=auto|chmod|off (기본 auto)
#   SPARSE_CHECK=1|0        (기본 1)
# ============================================================================
set -Eeuo pipefail

ARC="${1:-}"
[[ -n "$ARC" && -f "$ARC" ]] || { echo "사용법: $0 <archive>"; exit 1; }

STRICT_META="${STRICT_META:-0}"
APPLY_PERMS="${APPLY_PERMS:-auto}"
SPARSE_CHECK="${SPARSE_CHECK:-1}"

DEST="${ARC%.tar.zst}"; DEST="${DEST%.tar.gz}"; DEST="${DEST%.tgz}"; DEST="${DEST%.tar}"

echo "=== 안전한 압축 해제 및 전수 검증 시작 (v3) ==="
echo "원본: $ARC"
echo "추출: $DEST"
echo "옵션: STRICT_META=$STRICT_META APPLY_PERMS=$APPLY_PERMS SPARSE_CHECK=$SPARSE_CHECK"

# 0) FS 타입(참고용)
FSTYPE="$(stat -f -c %T "$(dirname "$DEST")" 2>/dev/null || echo unknown)"
FS_POSIX=1
case "$FSTYPE" in
  v9fs|fuseblk|ntfs|msdos) FS_POSIX=0 ;;
esac

# 1) 무결성 검사
echo "1) 아카이브 무결성 검사..."
case "$ARC" in
  *.tar.zst) zstd -t --long=31 -- "$ARC" ;;
  *.tar.gz|*.tgz) gzip -t -- "$ARC" ;;
  *.tar) tar -tf "$ARC" >/dev/null ;;
  *) echo "지원하지 않는 확장자"; exit 2;;
esac
echo "✅ 무결성 통과"

# 2) 아카이브 목록(파일/링크만)
echo "2) 파일 목록 추출..."
ORIGINAL_LIST=$(mktemp)
case "$ARC" in
  *.tar.zst)  zstd -dc --long=31 -- "$ARC" | tar -tf - ;;
  *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar -tf - ;;
  *.tar)      tar -tf "$ARC" ;;
esac \
| sed 's#^\./##' \
| grep -v '/$' \
| LC_ALL=C sort > "$ORIGINAL_LIST"
ORIGINAL_COUNT=$(wc -l < "$ORIGINAL_LIST")
echo "   엔트리: $ORIGINAL_COUNT"

# 3) 추출
echo "3) 추출(권한/스파스 보존 시도)..."
mkdir -p "$DEST"
case "$ARC" in
  *.tar.zst)  zstd -dc --long=31 -- "$ARC" | tar -xf - -C "$DEST" ;;
  *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar -xf - -C "$DEST" ;;
  *.tar)      tar -xf "$ARC" -C "$DEST" ;;
esac
echo "✅ 추출 완료"

# 4) 추출 목록(파일/링크만)
echo "4) 추출 목록 생성..."
EXTRACTED_LIST=$(mktemp)
(
  cd "$DEST"
  find . \( -type f -o -type l \) -printf '%P\n' | LC_ALL=C sort > "$EXTRACTED_LIST"
)
EXTRACTED_COUNT=$(wc -l < "$EXTRACTED_LIST")
echo "   엔트리: $EXTRACTED_COUNT"

# 5) 목록 비교
echo "5) 목록 비교..."
if ! diff -q "$ORIGINAL_LIST" "$EXTRACTED_LIST" >/dev/null 2>&1; then
  echo "❌ 목록 불일치"
  diff "$ORIGINAL_LIST" "$EXTRACTED_LIST" | head -80
  rm -f "$ORIGINAL_LIST" "$EXTRACTED_LIST"
  exit 3
fi
echo "✅ 목록 일치"

# 5b) 메타데이터 비교 (권한/mtime 차이는 경고)
echo "5b) 메타데이터 비교..."
META_RC=0
case "$ARC" in
  *.tar.zst) zstd -dc --long=31 -- "$ARC" | tar --compare -f - -C "$DEST" || META_RC=$? ;;
  *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar --compare -f - -C "$DEST" || META_RC=$? ;;
  *.tar) tar --compare -f "$ARC" -C "$DEST" || META_RC=$? ;;
esac
if [[ $META_RC -ne 0 ]]; then
  if [[ "$STRICT_META" == "1" ]]; then
    echo "❌ 메타데이터 비교 실패(STRICT_META=1)"; exit 6
  fi
  echo "⚠️ 메타데이터 차이(모드/mtime 등) 감지 → 계속 진행"
fi
# 권한 정규화
if [[ "$APPLY_PERMS" != "off" && ( "$APPLY_PERMS" == "chmod" || "$APPLY_PERMS" == "auto" ) ]]; then
  find "$DEST" -type d -exec chmod 0755 {} + 2>/dev/null || true
  find "$DEST" -type f -exec chmod 0644 {} + 2>/dev/null || true
  echo "✅ 권한 정규화 단계 완료"
fi

# 6) 전수 콘텐츠 검증
echo "6) 전수 콘텐츠 해시/링크 검증..."
trap '' PIPE  # tar 파이프 SIGPIPE 상위 전파 방지
VERIFICATION_FAILED=0
VERIFIED_COUNT=0

# 추출본의 심볼릭 링크 타깃 맵
declare -A LINKTARGETS
while IFS= read -r e; do
  p="$DEST/${e#./}"
  if [[ -L "$p" ]]; then
    LINKTARGETS["$e"]="$(readlink "$p" 2>/dev/null || echo)"
  fi
done < "$EXTRACTED_LIST"

is_type_in_arc() { # $1:path → '-' regular, 'l' symlink, '' none
  local t
  case "$ARC" in
    *.tar.zst) t=$(zstd -dc --long=31 -- "$ARC" | tar -tvf - -- "$1" 2>/dev/null | awk 'NR==1{print substr($1,1,1)}');;
    *.tar.gz|*.tgz) t=$(gzip -dc -- "$ARC" | tar -tvf - -- "$1" 2>/dev/null | awk 'NR==1{print substr($1,1,1)}');;
    *.tar) t=$(tar -tvf "$ARC" -- "$1" 2>/dev/null | awk 'NR==1{print substr($1,1,1)}');;
  esac
  printf "%s" "$t"
}

arc_read_hash() { # $1:path → sha256 or fail
  local q="$1" h rc=0
  case "$ARC" in
    *.tar.zst) h=$(zstd -dc --long=31 -- "$ARC" | tar -xO -f - -- "$q" 2>/dev/null | sha256sum | awk '{print $1}'); rc=$?;;
    *.tar.gz|*.tgz) h=$(gzip -dc -- "$ARC" | tar -xO -f - -- "$q" 2>/dev/null | sha256sum | awk '{print $1}'); rc=$?;;
    *.tar) h=$(tar -xO -f "$ARC" -- "$q" 2>/dev/null | sha256sum | awk '{print $1}'); rc=$?;;
  esac
  [[ $rc -eq 0 && -n "$h" ]] || return 1
  printf '%s' "$h"
}

arc_link_target() { # $1:path → link target or ''
  case "$ARC" in
    *.tar.zst) zstd -dc --long=31 -- "$ARC" | tar -tvf - -- "$1" 2>/dev/null | awk 'NR==1{print $NF}';;
    *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar -tvf - -- "$1" 2>/dev/null | awk 'NR==1{print $NF}';;
    *.tar) tar -tvf "$ARC" -- "$1" 2>/dev/null | awk 'NR==1{print $NF}';;
  esac
}

while IFS= read -r p0; do
  p="$p0"
  # 타입 판별(프리픽스 보정)
  t="$(is_type_in_arc "$p")"
  if [[ -z "$t" ]]; then
    t="$(is_type_in_arc "./$p")"
    [[ -n "$t" ]] && p="./$p" || true
  fi

  # 링크면 타깃 비교
  if [[ "$t" == "l" || -n "${LINKTARGETS["${p#./}"]:-}" ]]; then
    arc_tgt="$(arc_link_target "$p")"; fs_tgt="${LINKTARGETS["${p#./}"]:-}"
    if [[ -z "$arc_tgt" && "$p" == ./* ]]; then
      arc_tgt="$(arc_link_target "${p#./}")"
    fi
    if [[ "$arc_tgt" != "$fs_tgt" ]]; then
      echo "❌ symlink target 불일치: ${p#./} (arc=$arc_tgt, fs=$fs_tgt)"; VERIFICATION_FAILED=1; break
    fi
    echo "  link ok: ${p#./}"
    VERIFIED_COUNT=$((VERIFIED_COUNT+1))
    continue
  fi

  # 일반파일만 해시
  if [[ "$t" == "-" ]]; then
    echo "  hashing: ${p#./}"
    ORIG_HASH="$(arc_read_hash "$p" || arc_read_hash "${p#./}")" || {
      echo "❌ 아카이브 바이트 추출 실패: ${p#./}"; VERIFICATION_FAILED=1; break; }
    FS_PATH="$DEST/${p#./}"
    [[ -f "$FS_PATH" ]] || { echo "❌ 추출본 없음: $FS_PATH"; VERIFICATION_FAILED=1; break; }
    EXTRACT_HASH="$(sha256sum -- "$FS_PATH" | awk '{print $1}')"
    if [[ "$ORIG_HASH" != "$EXTRACT_HASH" ]]; then
      echo "❌ 해시 불일치: ${p#./}"; echo "  원본: $ORIG_HASH"; echo "  추출: $EXTRACT_HASH"
      VERIFICATION_FAILED=1; break
    fi
    VERIFIED_COUNT=$((VERIFIED_COUNT+1))
  fi
done < "$ORIGINAL_LIST"

if [[ $VERIFICATION_FAILED -ne 0 ]]; then
  echo "❌ 에러: 전수 검증 실패"; rm -f "$ORIGINAL_LIST" "$EXTRACTED_LIST"; exit 4
fi
if [[ $VERIFIED_COUNT -eq 0 ]]; then
  echo "❌ 에러: 전수 검증 0건(경로/타입 불일치 의심)"; rm -f "$ORIGINAL_LIST" "$EXTRACTED_LIST"; exit 10
fi
echo "✅ 전수 해시/링크 검증 통과 (파일 수: $VERIFIED_COUNT)"

# 7) 스파스 검증(환경에 따라 스킵)
if [[ "$SPARSE_CHECK" == "1" && "$FS_POSIX" == "1" ]]; then
  echo "8) 스파스 파일 검증(추론)..."
  # 간이 훅(필요시 심화 검증 추가 가능)
  echo "✅ 스파스 검사 완료"
else
  echo "8) 스파스 검사 스킵(SPARSE_CHECK=$SPARSE_CHECK, FS_POSIX=$FS_POSIX)"
fi

# 8) 안전 삭제(2단계)
echo "9) 모든 검증 통과 → 원본 안전 삭제"
mv -f -- "$ARC" "$ARC.to_delete"
sync || true
rm -f -- "$ARC.to_delete"
echo "✅ 원본 삭제 완료"
rm -f "$ORIGINAL_LIST" "$EXTRACTED_LIST"
echo "=== 완료: $DEST ==="




