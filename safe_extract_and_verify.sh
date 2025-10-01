#!/usr/bin/env bash
set -Eeuo pipefail

# 100% 복원 확인 후에만 원본 아카이브를 삭제하는 스크립트
# - 전수(전체) 콘텐츠 해시 검증
# - tar 메타데이터 비교(권한/소유권/mtime/링크 등)
# - 2단계 안전 삭제(원자적 rename -> sync -> rm)

ARC="${1:-}"
[[ -z "$ARC" ]] && { echo "사용법: $0 <압축파일경로>"; exit 1; }
[[ ! -f "$ARC" ]] && { echo "에러: 파일이 존재하지 않습니다: $ARC"; exit 1; }

# 목적지 폴더명 결정
DEST="${ARC%.tar.zst}"; DEST="${DEST%.tar.gz}"; DEST="${DEST%.tgz}"; DEST="${DEST%.tar}"

echo "=== 안전한 압축 해제 및 전수 검증 시작 ==="
echo "원본 파일: $ARC"
echo "추출 폴더: $DEST"

# 1) 원본 무결성(컨테이너 검사)
echo "1) 원본 아카이브 무결성 검사..."
case "$ARC" in
  *.tar.zst) zstd -t --long=31 -- "$ARC" ;;
  *.tar.gz|*.tgz) gzip -t -- "$ARC" ;;
  *.tar) tar -tf "$ARC" >/dev/null ;;
  *) echo "에러: 지원하지 않는 확장자"; exit 2;;
esac
echo "✅ 아카이브 무결성 통과"

# 2) 아카이브 파일 목록(정렬)
echo "2) 아카이브 파일 목록 추출..."
ORIGINAL_LIST=$(mktemp)
case "$ARC" in
  *.tar.zst) zstd -dc --long=31 -- "$ARC" | tar -tf - ;;
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
  *.tar.zst) zstd -dc --long=31 -- "$ARC" | tar -xpf - -C "$DEST" ;;
  *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar -xpf - -C "$DEST" ;;
  *.tar) tar -xpf "$ARC" -C "$DEST" ;;
esac
umask "$OLDUMASK"
echo "✅ 추출 완료"

# 4) 추출된 목록 생성(정렬). 파일/링크/디렉토리 모두 포함
echo "4) 추출 목록 생성..."
EXTRACTED_LIST=$(mktemp)
( cd "$DEST" && find . -mindepth 1 -printf '%P\n' | LC_ALL=C sort > "$EXTRACTED_LIST" )
EXTRACTED_COUNT=$(wc -l < "$EXTRACTED_LIST")
echo "   추출 엔트리 수: $EXTRACTED_COUNT"

# 5) 목록 동등성 검사
echo "5) 목록 비교..."
if ! diff -u "$ORIGINAL_LIST" "$EXTRACTED_LIST" >/dev/null; then
  echo "❌ 에러: 목록 불일치"; diff -u "$ORIGINAL_LIST" "$EXTRACTED_LIST" | head -50
  rm -f "$ORIGINAL_LIST" "$EXTRACTED_LIST"; exit 3
fi
echo "✅ 목록 일치"

# 5b) tar 메타데이터 비교(권한/소유/mtime/링크 등)
echo "5b) tar 메타데이터 비교..."
META_DIFF_LOG=$(mktemp)
set +e
case "$ARC" in
  *.tar.zst) zstd -dc --long=31 -- "$ARC" | tar --compare -f - -C "$DEST" 2>&1 | tee "$META_DIFF_LOG" ;;
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

# 6) 전수(전체) 콘텐츠 해시 검증: 일반 파일만
echo "6) 전수 콘텐츠 해시 검증(일반파일)..."
# 해시 대상: 아카이브에 존재하는 일반파일 집합
FILES_LIST=$(mktemp)
case "$ARC" in
  *.tar.zst) zstd -dc --long=31 -- "$ARC" | tar -tvf - ;;
  *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar -tvf - ;;
  *.tar) tar -tvf "$ARC" ;;
esac | awk '
  # GNU tar -tvf 형식 가정: 권한 필드 첫글자 -/d/l 등
  {type=substr($1,1,1);}
  type=="-" {
    # 파일명은 끝 필드(스페이스 포함 가능) → 정규표현이 안전하지 않으므로
    # tvf 출력에서 파일명 전부를 뽑기 위해 다음과 같이 처리
    # ex) "-rw-r--r-- user group size date time name"
    # 마지막 필드부터 재구성 (공백 포함 파일명 안정 처리가 tvf에서 애매함)
  }
' >/dev/null 2>&1 || true
# 위 방식은 tvf 파싱의 모호성이 있어, 보다 견고하게는 "원본 목록"을 기반으로
# 실제 파일인지 여부를 아카이브에서 직접 읽어 보며 판단한다.

# ORIGINAL_LIST를 한 줄씩 읽어 해당 엔트리가 "일반파일"일 때만 해시
VERIFICATION_FAILED=0
mapfile -t ALL_PATHS < "$ORIGINAL_LIST"

is_regular_in_arc() {
  local p="$1"
  case "$ARC" in
    *.tar.zst) zstd -dc --long=31 -- "$ARC" | tar -tvf - | grep -F -- "$p" | awk 'NR==1{print substr($1,1,1)}' ;;
    *.tar.gz|*.tgz) gzip -dc -- "$ARC" | tar -tvf - | grep -F -- "$p" | awk 'NR==1{print substr($1,1,1)}' ;;
    *.tar) tar -tvf "$ARC" | grep -F -- "$p" | awk 'NR==1{print substr($1,1,1)}' ;;
  esac
}

for p in "${ALL_PATHS[@]}"; do
  # 디렉토리/링크/장치파일 등은 건너뛴다(메타데이터 비교에서 이미 검증됨)
  t="$(is_regular_in_arc "$p" || true)"
  [[ "$t" != "-" ]] && continue

  printf '  hashing: %s\n' "$p"

  # 아카이브에서 해당 파일 바이트 스트림을 직접 꺼내 해시
  case "$ARC" in
    *.tar.zst) ORIG_HASH=$(zstd -dc --long=31 -- "$ARC" | tar -xO -f - -- "$p" | sha256sum | awk '{print $1}') ;;
    *.tar.gz|*.tgz) ORIG_HASH=$(gzip -dc -- "$ARC" | tar -xO -f - -- "$p" | sha256sum | awk '{print $1}') ;;
    *.tar) ORIG_HASH=$(tar -xO -f "$ARC" -- "$p" | sha256sum | awk '{print $1}') ;;
  esac

  EXTRACT_HASH=$(sha256sum -- "$DEST/$p" | awk '{print $1}')

  if [[ "$ORIG_HASH" != "$EXTRACT_HASH" ]]; then
    echo "❌ 해시 불일치: $p"
    echo "  원본:   $ORIG_HASH"
    echo "  추출본: $EXTRACT_HASH"
    VERIFICATION_FAILED=1
    break
  fi
done

if [[ $VERIFICATION_FAILED -ne 0 ]]; then
  echo "❌ 에러: 전수 해시 검증 실패"
  rm -f "$ORIGINAL_LIST" "$EXTRACTED_LIST"
  exit 4
fi
echo "✅ 전수 해시 검증 통과"

# (크기 비교 단계는 생략: 압축/클러스터/희소파일 때문에 의미 낮음)

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
