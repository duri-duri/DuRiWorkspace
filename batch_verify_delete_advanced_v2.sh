#!/usr/bin/env bash
# === Batch Verify & Delete v2 (final, patched) ==============================
# - 대상 아카이브를 병렬 처리로 "전수 검증 100% 통과 시만 삭제"
# - 마운트 공간가드(자동 추정), SIGPIPE 보정, 재시도, 실패격리, CSV요약
# - GNU parallel 사용 시 함수/환경 이슈 없이 동작하도록 헬퍼 스크립트 동적 생성
# 옵션:
#   -P N                   병렬도(기본 2)
#   --order size_asc|size_desc (기본 size_asc)
#   --retries N            실패 재시도(기본 1)
#   --space-guard PCT      여유%가 PCT 이하이면 대기(기본 0=off)
#   --space-mount PATH     공간가드 대상 마운트 지정(기본 자동)
#   --quarantine-dir DIR   실패본 격리 디렉토리(선택)
# 환경:
#   NICE(10), IONICE_CLASS(2), IONICE_LEVEL(7)
#   CSV(기본: 스크립트폴더/batch_summary_YYYY-MM-DD.csv)
#   INCL, EXCL             find 포함/제외 패턴(쉼표 구분)
# ============================================================================

set -Eeuo pipefail

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAFE="${SAFE:-$SELF_DIR/safe_extract_and_verify_v3.sh}"

PARALLEL=2
ORDER="size_asc"
RETRIES=1
SPACE_GUARD=0
SPACE_MOUNT=""
QUAR_DIR=""

# --- 간단 옵션 파서 ---
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -P|--parallel) PARALLEL="${2:-2}"; shift 2;;
    --order) ORDER="${2:-size_asc}"; shift 2;;
    --retries) RETRIES="${2:-1}"; shift 2;;
    --space-guard) SPACE_GUARD="${2:-0}"; shift 2;;
    --space-mount) SPACE_MOUNT="${2:-}"; shift 2;;
    --quarantine-dir|--quarantine) QUAR_DIR="${2:-}"; shift 2;;
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

# 헬퍼에 넘길 환경 변수 export
export SAFE CSV QUAR_DIR SPACE_GUARD SPACE_MOUNT NICE IONICE_CLASS IONICE_LEVEL

# CSV 경로 안내
echo "CSV 로그: $CSV"

# --- space-guard mount 추정/고정 ---
if [[ -z "$SPACE_MOUNT" ]]; then
  SPACE_MOUNT="$(df -P "$ROOT" 2>/dev/null | awk 'NR==2{print $6}')"
fi
if ! df -P "$SPACE_MOUNT" >/dev/null 2>&1; then
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
TMP_LIST="$(mktemp)"
TSV="$(mktemp)"
cleanup_files=("$TMP_LIST" "$TSV")

find "$ROOT" -type f \( -iname '*.tar' -o -iname '*.tgz' -o -iname '*.tar.gz' -o -iname '*.tar.zst' $( IFS=, ; for p in ${INCL:-}; do [[ -n "$p" ]] && printf ' -o -iname %q' "$p"; done ) \) \
  $( IFS=, ; for p in ${EXCL:-}; do [[ -n "$p" ]] && printf ' -not -iname %q' "$p"; done ) \
  -print0 > "$TMP_LIST"

while IFS= read -r -d '' f; do
  sz="$(stat -c%s "$f" 2>/dev/null || echo 0)"
  printf '%s\t%s\0' "$sz" "$f" >> "$TSV"
done < "$TMP_LIST"

# 정렬
SORTED0="$(mktemp)"; cleanup_files+=("$SORTED0")
case "$ORDER" in
  size_desc) sort -z -nr --field-separator=$'\t' --key=1,1 "$TSV" > "$SORTED0" ;;
  *)         sort -z -n  --field-separator=$'\t' --key=1,1 "$TSV" > "$SORTED0" ;;
esac
SORTED_LIST="$(mktemp)"; cleanup_files+=("$SORTED_LIST")
cut -z -f2 "$SORTED0" > "$SORTED_LIST"

TOTAL=$(tr -cd '\0' < "$SORTED_LIST" | wc -c)
echo "대상: $TOTAL 개 / 병렬: $PARALLEL / 순서: $ORDER / space-guard: ${SPACE_GUARD}%"

space_ok() { # $1:mnt $2:need%
  local used_pct free_pct
  used_pct="$(df -P "$1" 2>/dev/null | awk 'NR==2{print $5}' | tr -d '%')"
  [[ -z "$used_pct" ]] && return 0
  free_pct=$((100 - used_pct))
  (( free_pct > $2 ))
}

# CSV 헤더
if [[ ! -f "$CSV" ]]; then
  echo "ts,arc,status,rc,bytes,verified_count,dur_s" >> "$CSV"
fi

STOP_LAUNCH=0
trap 'echo "[INT] 중단 신호 → 신규 런칭 정지"; STOP_LAUNCH=1' INT TERM

# --- 실행 헬퍼(별도 파일로 동적 생성; GNU parallel/xargs 모두 동일 사용) ---
HELPER="$(mktemp)"
cleanup_files+=("$HELPER")
cat >"$HELPER" <<"__RUN_ONE__"
#!/usr/bin/env bash
set -Eeuo pipefail
arc="$1"
log="${arc}.verify.log"
start=$(date +%s)
size=$(stat -c%s "$arc" 2>/dev/null || echo 0)

# 공간 가드 체크
if [[ "${SPACE_GUARD:-0}" -gt 0 && -n "${SPACE_MOUNT:-}" ]]; then
  used_pct="$(df -P "$SPACE_MOUNT" 2>/dev/null | awk 'NR==2{print $5}' | tr -d '%')"
  if [[ -n "$used_pct" ]]; then
    free_pct=$((100 - used_pct))
    if (( free_pct <= SPACE_GUARD )); then
      echo "[WAIT] free% ≤ ${SPACE_GUARD} → 15s 대기" | tee -a "$log"
      sleep 15
    fi
  fi
fi

# 환경 변수로 들어오는 쉘 초기화 스크립트 무시(경고 억제)
if command -v ionice >/dev/null 2>&1; then
  env -u BASH_ENV -u ENV ionice -c "${IONICE_CLASS:-2}" -n "${IONICE_LEVEL:-7}" \
    nice -n "${NICE:-10}" bash "${SAFE:?SAFE not set}" "$arc" >>"$log" 2>&1 || rc=$?
else
  env -u BASH_ENV -u ENV nice -n "${NICE:-10}" \
    bash "${SAFE:?SAFE not set}" "$arc" >>"$log" 2>&1 || rc=$?
fi
rc="${rc:-0}"
end=$(date +%s); dur=$((end-start))

statustr="OK"; [[ $rc -ne 0 ]] && statustr="FAIL"
verc="$(grep -oP '파일 수:\s*\K[0-9]+' "$log" | tail -n1 || echo 0)"
ts="$(date +%FT%T)"

# CSV append (부모에서 CSV 경로 전달)
mkdir -p "$(dirname "$CSV")"
echo "$ts,\"$arc\",$statustr,$rc,$size,$verc,$dur" >> "${CSV:?CSV not set}"

# 실패 시 격리
if [[ $rc -ne 0 && -n "${QUAR_DIR:-}" ]]; then
  mkdir -p "$QUAR_DIR"
  ts2=$(date +%s)
  base_q="$(basename "$arc").fail.${rc}.${ts2}"
  echo "[QUAR] → $QUAR_DIR/$base_q" | tee -a "$log"
  mv -f -- "$arc" "$QUAR_DIR/$base_q" 2>>"$log" || true
fi

if [[ $rc -eq 0 ]]; then
  echo "[OK  ] $(date +%F\ %T) → $arc"
else
  # SIGPIPE(rc=141) 보정(로그 표시는 rc=1로 가정)
  if grep -q "SIGPIPE" "$log" 2>/dev/null; then
    echo "[INFO] SIGPIPE 보정(rc=141→1)" | tee -a "$log"
  fi
  echo "[FAIL] rc=$rc → $arc"
fi

exit "$rc"
__RUN_ONE__
chmod +x "$HELPER"

# --- 실행 ---
if command -v parallel >/dev/null 2>&1; then
  [[ $STOP_LAUNCH -eq 0 ]] || { echo "[INT] 런칭 스킵"; exit 130; }
  # GNU parallel: 환경(SAFE/CSV/QUAR_DIR/SPACE_*)을 상속받아 HELPER 실행
  parallel -0 -P "$PARALLEL" --lb --halt soon,fail=1 \
    "$HELPER" :::: "$SORTED_LIST"
else
  [[ $STOP_LAUNCH -eq 0 ]] || { echo "[INT] 런칭 스킵"; exit 130; }
  # xargs: NUL-세이프, -I{} 사용 시 -n 금지(경고 방지)
  xargs -0 -P "$PARALLEL" -I{} "$HELPER" {} < "$SORTED_LIST"
fi

# --- 간단 재시도 루프 ---
if [[ "$RETRIES" -gt 0 ]]; then
  for ((i=1;i<=RETRIES;i++)); do
    RETRY_LIST="$(mktemp)"; cleanup_files+=("$RETRY_LIST")
    awk -F, 'NR>1 && $3=="FAIL"{gsub(/^"|"$/,"",$2);print $2}' "$CSV" \
      | sort -u | tr '\n' '\0' > "$RETRY_LIST"
    RET_N=$(tr -cd '\0' < "$RETRY_LIST" | wc -c)
    [[ $RET_N -eq 0 ]] && break
    echo "[RETRY] 라운드 $i: $RET_N 개 재시도"

    if command -v parallel >/dev/null 2>&1; then
      parallel -0 -P "$PARALLEL" --lb --halt soon,fail=1 "$HELPER" :::: "$RETRY_LIST"
    else
      xargs -0 -P "$PARALLEL" -I{} "$HELPER" {} < "$RETRY_LIST"
    fi
  done
fi

echo "=== 배치 종료 ==="

# --- 정리 ---
for f in "${cleanup_files[@]}"; do rm -f "$f" 2>/dev/null || true; done
