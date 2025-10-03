#!/usr/bin/env bash
set -Euo pipefail
if locale -a 2>/dev/null | grep -qiE '^c\.utf-?8$'; then
  export LC_ALL=C.UTF-8; export LANG=C.UTF-8
else
  export LC_ALL=C; export LANG=C
fi

GT="${1:?usage: rag_eval.sh GT_TSV}"
K="${K:-3}"
SEARCH="${SEARCH:-scripts/rag_search.sh}"
RANK_FLAG="${RANK_FLAG:---rank}"
OUT="${OUT:-.reports/day62/eval_$(date +%F_%H%M).tsv}"
TIMEOUT_SECS="${TIMEOUT_SECS:-8}"
DEBUG_EVAL="${DEBUG_EVAL:-0}"

# 입력·매개변수 검증(친절 에러)
[[ -r "$GT" ]] || { echo "[eval] not readable: $GT" >&2; exit 2; }
[[ "$K" =~ ^[0-9]+$ && "$K" -gt 0 ]] || { echo "[eval] invalid K=$K" >&2; exit 2; }

mkdir -p "$(dirname "$OUT")"
printf "query\tk\thits\tp@k\tr@k\n" >"$OUT"

hit_sum=0; denom_k_sum=0; gold_sum=0; q_cnt=0

# 임시파일 트랩 설정
_tmpfiles=()
_cleanup(){ rm -f "${_tmpfiles[@]}" 2>/dev/null || true; }
trap _cleanup EXIT INT TERM

# 헤더/탭 검증(사소하지만 유용)
first="$(head -1 "$GT" | tr -d '\r')"
[[ "$first" == $'query\tcat\tpf\texpected_ids_csv' ]] || \
  echo "[eval] warning: unexpected header: [$first]" >&2

# GT를 FD로 직접 읽기 (파이프/프로세스치환 제거)
exec 3<"$GT"
IFS= read -r _header <&3 || true

while IFS= read -r line <&3 || [[ -n "${line:-}" ]]; do
  [[ -n "${line:-}" ]] && line=${line%$'\r'}                # CRLF 방어
  [[ -z "${line//[[:space:]]/}" ]] && continue              # 빈 줄 스킵

  # 빈 칼럼 보존: 라인→cut -f
  query=$(printf '%s' "$line" | cut -f1)
  cat=$(printf   '%s' "$line" | cut -f2)
  pf=$(printf    '%s' "$line" | cut -f3)
  expected=$(printf '%s' "$line" | cut -f4)

  ((q_cnt++))
  [[ "$DEBUG_EVAL" == "1" ]] && printf '[debug] q=[%s] c=[%s] p=[%s] e=[%s]\n' "$query" "$cat" "$pf" "$expected" >&2

  # gold / got 준비
  E="$(mktemp)"; G="$(mktemp)"; _tmpfiles+=("$E" "$G")
  printf '%s\n' "$expected" | tr ',' '\n' | sed -E 's/^[[:space:]]+|[[:space:]]+$//g;/^$/d' | sort -u >"$E"
  expected_cnt=$(wc -l <"$E" | tr -d ' ')

  args=( "$query" $RANK_FLAG --k "$K" --format ids )
  [[ -n "${cat//[[:space:]]/}" ]] && args+=( --cat "$cat" )
  [[ -n "${pf//[[:space:]]/}"  ]] && args+=( --pf  "$pf"  )

  # 검색 실행 → sed/정리 → $G 저장, 그리고 '생산자(첫 명령)의 종료코드'를 PIPESTATUS[0]로 받음
  if command -v timeout >/dev/null 2>&1; then
    timeout "$TIMEOUT_SECS" bash "$SEARCH" "${args[@]}" \
      | sed -E 's/^[[:space:]]+|[[:space:]]+$//g;/^$/d' \
      | sort -u >"$G"
    # NOTE: rc는 '생산자(검색 명령)의 종료코드'를 PIPESTATUS[0]에서 받는다.
    rc=${PIPESTATUS[0]}
  else
    bash "$SEARCH" "${args[@]}" \
      | sed -E 's/^[[:space:]]+|[[:space:]]+$//g;/^$/d' \
      | sort -u >"$G"
    rc=${PIPESTATUS[0]}
  fi

  # 실패(타임아웃/에러)면 해당 쿼리는 '결과 없음'으로 처리
  [[ ${rc:-0} -ne 0 ]] && : >"$G"   # 실패/타임아웃이면 빈 결과로 처리(스코어 0)

  # 지표
  hits=$(comm -12 "$E" "$G" | wc -l | tr -d ' ')
  hit_sum=$((hit_sum + hits))
  denom_k_sum=$((denom_k_sum + K))
  gold_sum=$((gold_sum + expected_cnt))

  p=$(awk -v h="$hits" -v k="$K" 'BEGIN{printf("%.4f",(k? h/k:0))}')
  r=$(awk -v h="$hits" -v e="$expected_cnt" 'BEGIN{printf("%.4f",(e? h/e:0))}')
  printf "%s\t%s\t%s\t%s\t%s\n" "$query" "$K" "$hits" "$p" "$r" >>"$OUT"

  if [[ "$DEBUG_EVAL" == "1" ]]; then
    echo "[debug] gold:" >&2; cat "$E" >&2
    echo "[debug] got:"  >&2; cat "$G" >&2
    echo "[debug] hits=$(comm -12 "$E" "$G" | paste -sd, -)" >&2
  fi
  rm -f "$E" "$G"
done
exec 3<&-

# 데이터 한 줄도 못 돌았으면 명시적 실패
if [[ $q_cnt -eq 0 ]]; then
  echo "[eval] no data rows processed: check TSV/header/CRLF" >&2
  exit 3
fi

{
  echo '---'
  printf "queries\t%s\n" "$q_cnt"
  micro_p=$(awk -v h="$hit_sum" -v d="$denom_k_sum" 'BEGIN{printf("%.4f",(d? h/d:0))}')
  micro_r=$(awk -v h="$hit_sum" -v g="$gold_sum" 'BEGIN{printf("%.4f",(g? h/g:0))}')
  printf "micro_p@%s\t%s\n" "$K" "$micro_p"
  printf "micro_r@%s\t%s\n" "$K" "$micro_r"

  # 데이터셋 무결성 표시
  gt_hash=$(md5sum "$GT" | awk '{print $1}')
  printf "gt_md5\t%s\n" "$gt_hash"

  # 재현 정보 스탬프
  printf "commit\t%s\n" "$(git rev-parse --short HEAD 2>/dev/null || echo n/a)"
  printf "locale\t%s\n" "${LC_ALL:-${LANG:-n/a}}"
} >>"$OUT"

# OUT.jsonl 병행 기록 (CI 대시보드/스프레드시트 연동 편의)
printf '{"ts":"%s","k":%s,"queries":%s,"micro_p":%s,"micro_r":%s}\n' \
  "$(date -Is)" "$K" "$q_cnt" "$micro_p" "$micro_r" >> "${OUT%.tsv}.jsonl"

cat "$OUT"
