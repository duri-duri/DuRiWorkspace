#!/usr/bin/env bash
set -Eeuo pipefail

# 여러 .tar(.zst/.gz/.tgz) 아카이브를 100% 검증 후 안전 삭제(개별 독립)하는 고급 배치 래퍼
# - safe_extract_and_verify_v2.sh 를 호출한다(같은 디렉터리에 있다고 가정).
# - GNU parallel 존재 시 parallel, 없으면 xargs -P 로 병렬 처리.
# - OK/FAIL 마커를 남겨 재실행 시 건너뛰기.
# - 모든 경로 공백/한글 안전(null-구분).
# - 공간 가드, 재시도, 자원 통제 포함

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAFE="${SAFE:-"$SELF_DIR/safe_extract_and_verify_v2.sh"}"
[[ -x "$SAFE" ]] || { echo "에러: 실행 불가 $SAFE"; exit 1; }

ROOT="${1:-.}"
PARALLEL="${P:-5}"           # 병렬 수
ORDER="${ORDER:-size_desc}"  # size_desc|size_asc|name
RETRIES="${RETRIES:-2}"      # 실패 재시도 횟수(추가 시도 수)
BACKOFF_BASE="${BACKOFF_BASE:-3}" # 초
SPACE_GUARD_PCT="${SPACE_GUARD_PCT:-10}"   # 남은 용량 % 미만이면 대기
SPACE_GUARD_MNT="${SPACE_GUARD_MNT:-$ROOT}"  # 감시 대상 마운트 루트(기본 ROOT)
SPACE_POLL_SEC="${SPACE_POLL_SEC:-20}"     # 대기 중 재확인 주기(초)
NICE="${NICE:-10}"
IONICE_CLASS="${IONICE_CLASS:-2}"
IONICE_LEVEL="${IONICE_LEVEL:-7}"
export ZSTD_NBTHREADS="${ZSTD_NBTHREADS:-1}"

# 옵션 파싱(간단)
while [[ $# -gt 0 ]]; do
  case "$1" in
    -P|--parallel) PARALLEL="${2:-5}"; shift 2;;
    --order) ORDER="${2:-size_desc}"; shift 2;;
    --retries) RETRIES="${2:-2}"; shift 2;;
    --space-guard) SPACE_GUARD_PCT="${2:-10}"; shift 2;;
    --space-mount) SPACE_GUARD_MNT="${2:-$ROOT}"; shift 2;;
    -h|--help)
      cat <<EOF
사용법: $0 [스캔루트] [-P N] [--order size_desc|size_asc|name] [--retries N] [--space-guard PCT] [--space-mount PATH]
환경:
  SAFE=<path>      # safe_extract_and_verify_v2.sh 경로(기본: 현재 스크립트 옆)
  P=<N>            # 병렬도(옵션 -P와 동일, 기본 5)
  ORDER=<정렬키>   # 기본 size_desc
  RETRIES=<N>      # 재시도 횟수(기본 2)
  SPACE_GUARD_PCT=<N>  # 공간 가드 임계치 %(기본 10)
  SPACE_GUARD_MNT=<PATH>  # 공간 감시 마운트(기본 ROOT)
EOF
      exit 0;;
    *)
      if [[ -z "${ROOT_SET:-}" ]]; then
        ROOT="$1"
        ROOT_SET=1
      fi
      shift;;
  esac
done

LOGDIR="${LOGDIR:-$SELF_DIR/logs}"
STATEDIR="${STATEDIR:-$SELF_DIR/state}"
mkdir -p "$LOGDIR" "$STATEDIR"

echo "=== 고급 배치 아카이브 처리 시작 ==="
echo "스캔 루트: $ROOT"
echo "병렬도: $PARALLEL"
echo "처리 순서: $ORDER"
echo "재시도 횟수: $RETRIES"
echo "공간 가드: < ${SPACE_GUARD_PCT}% (마운트: $SPACE_GUARD_MNT)"

# null-구분 목록 작성
TMP_LIST="$(mktemp)"
find "$ROOT" -type f \( -iname '*.tar' -o -iname '*.tar.zst' -o -iname '*.tar.gz' -o -iname '*.tgz' \) -print0 > "$TMP_LIST"

# 정렬 함수(null-구분)
sort_null_by() {
  case "$ORDER" in
    size_desc)
      awk -v RS='\0' -v ORS='\0' '
        function statsize(p,  cmd, s) {
          cmd="stat -c%s " q p q; cmd | getline s; close(cmd); return s
        }
        BEGIN{ q="\047" }
        { sz=statsize($0); printf "%020d\t%s%c", (sz+0), $0, 0 }
      ' < "$TMP_LIST" | LC_ALL=C sort -zr -k1,1 | awk -v RS='\0' -v ORS='\0' -F'\t' '{print $2}'
      ;;
    size_asc)
      awk -v RS='\0' -v ORS='\0' '
        function statsize(p,  cmd, s) {
          cmd="stat -c%s " q p q; cmd | getline s; close(cmd); return s
        }
        BEGIN{ q="\047" }
        { sz=statsize($0); printf "%020d\t%s%c", (sz+0), $0, 0 }
      ' < "$TMP_LIST" | LC_ALL=C sort -z -k1,1 | awk -v RS='\0' -v ORS='\0' -F'\t' '{print $2}'
      ;;
    name) LC_ALL=C sort -z < "$TMP_LIST" ;;
    *)    LC_ALL=C sort -zr < "$TMP_LIST" ;;
  esac
}
SORTED_LIST="$(mktemp)"; sort_null_by > "$SORTED_LIST"

# 남은 용량 % 계산
free_pct() {
  local p="${1:-/}"
  # df 출력(%)에서 숫자만 추출
  df -P "$p" 2>/dev/null | awk 'NR==2{gsub("%","",$5); used=$5; print 100-used}' || echo "100"
}

# 공간 가드: 임계 미만이면 대기
space_guard_wait() {
  while :; do
    local pct
    pct="$(free_pct "$SPACE_GUARD_MNT")"
    pct="${pct%.*}"
    if [[ "${pct:-0}" -lt "$SPACE_GUARD_PCT" ]]; then
      echo "[SPACE] 여유 ${pct}% < 임계 ${SPACE_GUARD_PCT}% → ${SPACE_POLL_SEC}s 대기..."
      sleep "$SPACE_POLL_SEC"
    else
      break
    fi
  done
}

run_one() {
  local arc="$1"
  local base; base="$(basename "$arc")"
  local mark_ok="$STATEDIR/${base}.ok"
  local mark_fail="$STATEDIR/${base}.fail"
  local lock="$STATEDIR/${base}.lock"
  local log="$LOGDIR/${base}.log"

  [[ -f "$mark_ok" ]] && { echo "[SKIP] OK: $arc"; return 0; }

  exec 9>"$lock" || true
  if ! flock -n 9; then
    echo "[LOCK] 동시 처리 중: $arc"; return 0
  fi

  local attempt=0 rc=1
  : > "$log"

  while (( attempt <= RETRIES )); do
    space_guard_wait
    echo "[RUN ] $(date +'%F %T') try=$((attempt+1)) → $arc" | tee -a "$log"

    if command -v ionice >/dev/null 2>&1; then
      ionice -c "$IONICE_CLASS" -n "$IONICE_LEVEL" nice -n "$NICE" bash "$SAFE" "$arc" >>"$log" 2>&1 || rc=$?
    else
      nice -n "$NICE" bash "$SAFE" "$arc" >>"$log" 2>&1 || rc=$?
    fi

    if [[ "${rc:-0}" -eq 0 ]]; then
      echo "[OK  ] $(date +'%F %T') → $arc" | tee -a "$log"
      : > "$mark_ok"; [[ -f "$mark_fail" ]] && rm -f "$mark_fail"
      return 0
    fi

    echo "[FAIL] rc=$rc (try=$((attempt+1))/${RETRIES+1}) → $arc" | tee -a "$log"
    if (( attempt < RETRIES )); then
      backoff=$(( BACKOFF_BASE << attempt ))   # 3,6,12,...
      echo "[WAIT] 재시도 전 ${backoff}s 대기" | tee -a "$log"
      sleep "$backoff"
    fi
    attempt=$((attempt+1))
  done

  : > "$mark_fail"
  return "$rc"
}
export -f run_one space_guard_wait free_pct
export SAFE LOGDIR STATEDIR NICE IONICE_CLASS IONICE_LEVEL \
       SPACE_GUARD_PCT SPACE_GUARD_MNT SPACE_POLL_SEC BACKOFF_BASE RETRIES

TOTAL=$(tr -cd '\0' < "$SORTED_LIST" | wc -c)
echo "대상: $TOTAL 개 / 병렬: $PARALLEL / 순서: $ORDER / 공간가드: < ${SPACE_GUARD_PCT}%"

if command -v parallel >/dev/null 2>&1; then
  echo "GNU parallel 사용"
  parallel -0 -P "$PARALLEL" --bar run_one ::: "$(cat "$SORTED_LIST")"
else
  echo "xargs 사용"
  xargs -0 -P "$PARALLEL" -I{} bash -lc 'run_one "$@"' _ {} < "$SORTED_LIST"
fi

OKS=$(ls -1 "$STATEDIR"/*.ok 2>/dev/null | wc -l || echo 0)
FAILS=$(ls -1 "$STATEDIR"/*.fail 2>/dev/null | wc -l || echo 0)
echo "=== 요약 ==="
echo "OK   : $OKS"
echo "FAIL : $FAILS"
[[ "$FAILS" -gt 0 ]] && { echo "--- 실패 목록 ---"; ls -1 "$STATEDIR"/*.fail 2>/dev/null | sed 's#.*/##;s/\.fail$//' ; }

rm -f "$TMP_LIST" "$SORTED_LIST"
