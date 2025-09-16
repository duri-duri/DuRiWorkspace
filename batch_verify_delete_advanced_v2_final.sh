#!/usr/bin/env bash
# === Batch Verify & Delete v2 (final) ======================================
# - 대상 아카이브를 병렬 처리로 "전수 검증 100% 통과 시만 삭제"
# - 마운트 공간가드(자동 추정), SIGPIPE 보정, 재시도, 실패격리, CSV요약
# 옵션:
#   -P N                   병렬도(기본 2)
#   --order size_asc|size_desc (기본 size_asc)
#   --retries N            실패 재시도(기본 1)
#   --space-guard PCT      여유%가 PCT 이하이면 대기(기본 0=off)
#   --space-mount PATH     공간가드 대상 마운트 지정(기본 자동)
#   --quarantine-dir DIR   실패본 격리 디렉토리(선택)
# 환경:
#   NICE(10), IONICE_CLASS(2), IONICE_LEVEL(7), CSV(기본: 스크립트폴더/batch_summary_YYYY-MM-DD.csv)
#   INCL, EXCL             find 포함/제외 패턴(쉼표로 구분, 예: INCL="*.tar.bz2", EXCL="*test*.tar.gz")
# ============================================================================
set -Eeuo pipefail

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAFE="${SAFE:-$SELF_DIR/safe_extract_and_verify_v3_final.sh}"

PARALLEL=2
ORDER="size_asc"
RETRIES=1
SPACE_GUARD=0
SPACE_MOUNT=""
QUAR_DIR=""

# --- getopt 대체 파싱 ---
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -P) PARALLEL="${2:-2}"; shift 2;;
    --order) ORDER="${2:-size_asc}"; shift 2;;
    --retries) RETRIES="${2:-1}"; shift 2;;
    --space-guard) SPACE_GUARD="${2:-0}"; shift 2;;
    --space-mount) SPACE_MOUNT="${2:-}"; shift 2;;
    --quarantine-dir) QUAR_DIR="${2:-}"; shift 2;;
    --) shift; break;;
    -*)
      echo "알 수 없는 옵션: $1"; exit 1;;
    *) ARGS+=("$1"); shift;;
  esac
done
ROOT="${ARGS[0]:-}"
[[ -n "$ROOT" && -d "$ROOT" ]] || { echo "사용법: $0 [옵션] <scan_root>"; exit 1; }

NICE="${NICE:-10}"
IONICE_CLASS="${IONICE_CLASS:-2}"
IONICE_LEVEL="${IONICE_LEVEL:-7}"
CSV="${CSV:-$SELF_DIR/batch_summary_$(date +%F).csv}"

echo "=== 고급 배치 아카이브 처리 (v2) ==="

# --- space-guard mount 추정/고정 ---
SPACE_MOUNT="${SPACE_MOUNT:-}"
if [[ -z "$SPACE_MOUNT" ]]; then
  SPACE_MOUNT="$(df -P "$ROOT" 2>/dev/null | awk 'NR==2{print $6}')"
fi
if [[ -z "$SPACE_MOUNT" || ! $(df -P "$SPACE_MOUNT" 2>/dev/null) ]]; then
  echo "공간 가드: 비활성화"
  SPACE_GUARD=0
else
  if [[ "${SPACE_GUARD:-0}" -gt 0 ]]; then
    echo "공간 가드: < ${SPACE_GUARD}% (마운트: $SPACE_MOUNT)"
  else
    echo "공간 가드: 비활성화"
  fi
fi

echo "스캔 루트: $ROOT"
echo "병렬도: $PARALLEL"
echo "처리 순서: $ORDER"
echo "재시도 횟수: $RETRIES"

# --- 대상 수집 ---
TMP_LIST="$(mktemp)"       # 0-구분 생목록
TSV="$(mktemp)"            # size\tpath 목록

# 기본 확장자 + INCL
find "$ROOT" -type f \( -iname '*.tar' -o -iname '*.tgz' -o -iname '*.tar.gz' -o -iname '*.tar.zst' $( \
  IFS=, ; for p in ${INCL:-}; do [[ -n "$p" ]] && printf ' -o -iname %q' "$p"; done ) \) \
  $( IFS=, ; for p in ${EXCL:-}; do [[ -n "$p" ]] && printf ' -not -iname %q' "$p"; done ) \
  -print0 > "$TMP_LIST"

# 사이즈 수집
while IFS= read -r -d '' f; do
  sz="$(stat -c%s "$f" 2>/dev/null || echo 0)"
  printf '%s\t%s\0' "$sz" "$f" >> "$TSV"
done < "$TMP_LIST"

# 정렬
SORTED0="$(mktemp)"
case "$ORDER" in
  size_desc)  sort -z -nr --field-separator=$'\t' --key=1,1 "$TSV" > "$SORTED0" ;;
  *)          sort -z -n  --field-separator=$'\t' --key=1,1 "$TSV" > "$SORTED0" ;;
esac
SORTED_LIST="$(mktemp)"
cut -z -f2 "$SORTED0" > "$SORTED_LIST"

# 통계
TOTAL=$(tr -cd '\0' < "$SORTED_LIST" | wc -c)
echo "대상: $TOTAL 개 / 병렬: $PARALLEL / 순서: $ORDER / space-guard: ${SPACE_GUARD}%"

# --- 보조 함수 ---
space_ok() {
  local mnt="$1" need="$2" used_pct free_pct
  used_pct="$(df -P "$mnt" 2>/dev/null | awk 'NR==2{print $5}' | tr -d '%')"
  [[ -z "$used_pct" ]] && return 0
  free_pct=$((100 - used_pct))
  (( free_pct > need ))
}

# CSV 헤더
if [[ ! -f "$CSV" ]]; then
  echo "ts,arc,status,rc,bytes,verified_count,dur_s" >> "$CSV"
fi

STOP_LAUNCH=0
trap 'echo "[INT] 중단 신호 → 신규 런칭 정지"; STOP_LAUNCH=1' INT TERM

run_one() {
  local arc="$1"
  local log="${arc}.verify.log"
  local start end dur size rc statustr verc ts

  if [[ "${SPACE_GUARD:-0}" -gt 0 && -n "$SPACE_MOUNT" ]]; then
    if ! space_ok "$SPACE_MOUNT" "$SPACE_GUARD"; then
      echo "[WAIT] free% ≤ ${SPACE_GUARD} → 15s 대기"
      sleep 15
    fi
  fi

  start=$(date +%s)
  size=$(stat -c%s "$arc" 2>/dev/null || echo 0)

  (
    set +o pipefail
    if command -v ionice >/dev/null 2>&1; then
      ionice -c "$IONICE_CLASS" -n "$IONICE_LEVEL" nice -n "$NICE" bash "$SAFE" "$arc" >>"$log" 2>&1
    else
      nice -n "$NICE" bash "$SAFE" "$arc" >>"$log" 2>&1
    fi
  )
  rc=$?
  end=$(date +%s); dur=$((end-start))
  statustr="OK"; [[ $rc -ne 0 ]] && statustr="FAIL"

  # 전수 검증 카운트 추출
  verc=$(grep -oE '전수 (해시|해시/링크) 검증 통과 \(파일 수: [0-9]+' "$log" | awk '{print $6}' | tr -d ')' || echo 0)

  ts="$(date +%FT%T)"
  echo "$ts,\"$arc\",$statustr,$rc,$size,$verc,$dur" >> "$CSV"

  if [[ $rc -ne 0 && -n "$QUAR_DIR" ]]; then
    mkdir -p "$QUAR_DIR"
    ts2=$(date +%s)
    base_q="$(basename "$arc").fail.${rc}.${ts2}"
    echo "[QUAR] → $QUAR_DIR/$base_q" | tee -a "$log"
    mv -f -- "$arc" "$QUAR_DIR/$base_q" 2>>"$log" || true
  fi

  if [[ $rc -eq 0 ]]; then
    echo "[OK  ] $(date +%F\ %T) → $arc"
  else
    echo "[FAIL] rc=$rc → $arc"
  fi

  return $rc
}

# --- 실행 ---
if command -v parallel >/dev/null 2>&1; then
  [[ $STOP_LAUNCH -eq 0 ]] || { echo "[INT] 런칭 스킵"; exit 130; }
  # GNU parallel은 NUL 안전. 입력을 펼쳐서 넘김.
  parallel -0 -P "$PARALLEL" --lb --halt soon,fail=1 run_one ::: "$(cat "$SORTED_LIST")"
else
  [[ $STOP_LAUNCH -eq 0 ]] || { echo "[INT] 런칭 스킵"; exit 130; }
  # xargs: -I{} 사용 시 -n은 사용 금지(경고 방지). NUL 안전.
  xargs -0 -P "$PARALLEL" -I{} bash -lc 'set +o pipefail; run_one "$1"' _ {} < "$SORTED_LIST"
fi

# --- 간단 재시도 루프 ---
if [[ "$RETRIES" -gt 0 ]]; then
  for ((i=1;i<=RETRIES;i++)); do
    # 실패 로그에서 실패 대상만 추출
    RETRY_LIST="$(mktemp)"
    awk -F, 'NR>1 && $3=="FAIL"{gsub(/^"|"$/,"",$2);print $2}' "$CSV" \
      | sort -u | tr '\n' '\0' > "$RETRY_LIST"
    RET_N=$(tr -cd '\0' < "$RETRY_LIST" | wc -c)
    [[ $RET_N -eq 0 ]] && break
    echo "[RETRY] 라운드 $i: $RET_N 개 재시도"

    if command -v parallel >/dev/null 2>&1; then
      parallel -0 -P "$PARALLEL" --lb --halt soon,fail=1 run_one ::: "$(cat "$RETRY_LIST")"
    else
      xargs -0 -P "$PARALLEL" -I{} bash -lc 'set +o pipefail; run_one "$1"' _ {} < "$RETRY_LIST"
    fi
  done
fi

echo "=== 배치 종료 ==="



