#!/usr/bin/env bash
set -Eeuo pipefail

echo "Hello from migrate_full_apply.sh"
echo "현재 시간: $(date)"
echo "작업 디렉토리: $(pwd)"

### [Config]
META_DEFAULT="/mnt/usb/CORE_PROTECTED/META"
HDD_DEFAULT="/mnt/hdd"
DEST_SUB="ARCHIVE/FULL"
APPLY_DEFAULT="0"

META="${META:-$META_DEFAULT}"
HDD="${HDD:-$HDD_DEFAULT}"
DEST="${DEST:-$HDD/$DEST_SUB}"
APPLY="${APPLY:-$APPLY_DEFAULT}"

echo "설정 완료:"
echo "  META=$META"
echo "  HDD=$HDD"
echo "  DEST=$DEST"
echo "  APPLY=$APPLY"

### [Utils]
log(){ printf "[%s] %s\n" "$(date +%F_%T)" "$*"; }
die(){ log "ERROR: $*"; exit 1; }
need_file(){ [ -f "$1" ] || die "missing file: $1"; }
need_cmd(){ command -v "$1" >/dev/null 2>&1 || die "need cmd: $1"; }

echo "유틸리티 함수 추가 완료"

### [Preflight]
echo "사전 검증 시작..."

# 필수 명령어 확인
need_cmd jq
need_cmd rsync
echo "✅ 필수 명령어 확인 완료"

# 필수 파일 확인
IDX="$META/INDEX.full.normalized.jsonl"
DEDUP="$META/REPORT.dedup.json"
GOLD="$META/REPORT.gold.json"

need_file "$IDX"
need_file "$GOLD"
echo "✅ 필수 파일 확인 완료"

# DEDUP는 없을 수도 있음(중복이 없으면)
[ -f "$DEDUP" ] || { echo "no DEDUP report found (ok)"; printf '[]' > "$DEDUP"; }

# HDD 경로 준비(미마운트면 DRY 권장)
if ! mount | grep -q " $HDD"; then
  echo "WARN: $HDD not mounted (continuing; DRY mode recommended)"
fi

if [ "$APPLY" = "1" ]; then mkdir -p "$DEST" || die "cannot create $DEST"; else log "[DRY] skip mkdir $DEST"; fi
echo "✅ HDD 경로 준비 완료"

echo "사전 검증 완료!"

### [Build copy lists]
echo "복사 목록 생성 시작..."

TMP_ALL=$(mktemp)
TMP_DUP=$(mktemp)
TMP_TODO=$(mktemp)
TMP_GOLD=$(mktemp)
TMP_REST=$(mktemp)

jq -r '.src' "$IDX" > "$TMP_ALL"
jq -r '.[].dups[]?' "$DEDUP" > "$TMP_DUP" || true
grep -vxF -f "$TMP_DUP" "$TMP_ALL" > "$TMP_TODO"

jq -r '.[].gold' "$GOLD" > "$TMP_GOLD"
grep -vxF -f "$TMP_GOLD" "$TMP_TODO" > "$TMP_REST"

echo "복사 목록 생성 완료:"
echo "  전체: $(wc -l < "$TMP_TODO")개"
echo "  GOLD: $(wc -l < "$TMP_GOLD")개"
echo "  나머지: $(wc -l < "$TMP_REST")개"

### [Copy helper]
copy_list(){
  local list="$1" label="$2"
  local n=0
  while IFS= read -r SRC; do
    [ -n "${SRC:-}" ] || continue
    if [ "$APPLY" = "1" ]; then
      echo "[APPLY:$label] $SRC -> $DEST/"
      rsync --mkpath --ignore-existing -avh "$SRC" "$DEST/"
    else
      echo "[DRY:$label] $SRC -> $DEST/"
    fi
    n=$((n+1))
  done < "$list"
  echo "$label 복사 완료 (계획): $n개"
}

echo "복사 함수 추가 완료"

### [Execute copy]
echo "복사 실행 시작..."

# 1) GOLD 우선 복사
echo "�� GOLD 백업 우선 복사..."
copy_list "$TMP_GOLD" "GOLD"

# 2) 나머지 백업 복사
echo "�� 나머지 백업 복사..."
copy_list "$TMP_REST" "REST"

echo "복사 실행 완료!"

### [Final Report]
echo ""
echo "🎯 이관 완료 요약"
echo "=================="
echo "모드: $([ "$APPLY" = "1" ] && echo "APPLY" || echo "DRY")"
echo "총 대상: $(wc -l < "$TMP_TODO")개"
echo "GOLD 백업: $(wc -l < "$TMP_GOLD")개"
echo "나머지 백업: $(wc -l < "$TMP_REST")개"
echo "대상 경로: $DEST"
echo ""

if [ "$APPLY" = "1" ]; then
  echo "✅ HDD 이관이 완료되었습니다!"
  echo "�� 무결성 검증을 위해 다음 명령어를 실행하세요:"
  echo "  pushd $DEST && sha256sum -c /tmp/SHA256SUMS.to_verify.txt"
else
  echo "📋 DRY-RUN이 완료되었습니다."
  echo "실제 이관을 원하면: APPLY=1 $0"
fi

echo ""
echo " 8월 20일 아침 상황에서 이어서 진행 완료!"

### [TODO: Dedup 용량 계산]
# 나중에 HDD 붙이기 전에 실제 필요 용량(중복 제외) 계산을 자동화할 때 사용
#
# META=/mnt/usb/CORE_PROTECTED/META
#
# # 전체 용량 합계
# TOTAL_BYTES=$(jq -s 'map(.bytes) | add' "$META/INDEX.full.normalized.jsonl")
# TOTAL_GB=$(echo "scale=2; $TOTAL_BYTES / 1024 / 1024 / 1024" | bc -l)
# echo "총 용량: $TOTAL_GB GB ($TOTAL_BYTES bytes)"
#
# # 중복된 파일 용량 합계
# DUP_BYTES=$(jq -s '
#   (.[0] | INDEX(.src)) as $idx
#   | (.[1] | map(.dups[]?) | flatten | unique)
#   | map($idx[.]?.bytes // 0) | add // 0
# ' "$META/INDEX.full.normalized.jsonl" "$META/REPORT.dedup.json")
#
# DUP_GB=$(echo "scale=2; $DUP_BYTES / 1024 / 1024 / 1024" | bc -l)
# echo "중복 용량: $DUP_GB GB ($DUP_BYTES bytes)"
#
# # 실제 필요 용량 (중복 제외)
# ACTUAL_BYTES=$((TOTAL_BYTES - DUP_BYTES))
# ACTUAL_GB=$(echo "scale=2; $ACTUAL_BYTES / 1024 / 1024 / 1024" | bc -l)
# echo "실제 필요 용량: $ACTUAL_GB GB ($ACTUAL_BYTES bytes)"
