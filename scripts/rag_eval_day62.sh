#!/usr/bin/env bash
set -euo pipefail

# python 명령 해결
export PATH="$HOME/.local/bin:$PATH"

GT="${1:-.reports/day62/ground_truth.tsv}"
K="${K:-3}"
SEARCH_SCRIPT="${SEARCH_SCRIPT:-scripts/rag_search_day62_final.sh}"

echo "🔍 RAG 검색 품질 평가 (Day 62)"
echo "Ground Truth: ${GT}"
echo "Precision@k with k=${K}"
echo "검색 스크립트: ${SEARCH_SCRIPT}"
echo

ts="$(date +%F_%H%M)"
OUT=".reports/day62/eval_${ts}.tsv"
mkdir -p .reports/day62
printf "query\tk\thits\tp@k\tr@k\n" > "$OUT"

total_queries=0
total_hits=0
total_expected=0
# 분모는 항상 '쿼리 수 × K'로 고정(검색결과가 적게 나와도 분모는 K로 계산)
total_results=0
macro_p_sum=0
macro_r_sum=0

# 공백/탭 모두를 구분자로 보며, 부족한 열(cat/pf) 있어도 OK
# 첫 열=query, 마지막 열=expected_ids_csv 로 해석
while IFS= read -r line || [[ -n "${line:-}" ]]; do
  # 공백/주석 스킵
  [[ -z "${line//[[:space:]]/}" ]] && continue
  [[ "${line:0:1}" == "#" ]] && continue

  # 필드 파싱(탭/스페이스 혼용 안전)
  query=$(awk 'BEGIN{FS="[ \t]+"} {print $1}' <<< "$line")
  expected_csv=$(awk 'BEGIN{FS="[ \t]+"} {print $NF}' <<< "$line")
  cat_field=$(awk 'BEGIN{FS="[ \t]+"} {if(NF>=3)print $2; else print ""}' <<< "$line")
  pf_field=$(awk 'BEGIN{FS="[ \t]+"} {if(NF>=4)print $3; else print ""}' <<< "$line")

  # 기대 집합
  E="$(mktemp)"; G="$(mktemp)"; trap 'rm -f "$E" "$G"' RETURN
  printf '%s\n' "$expected_csv" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | LC_ALL=C sort -u > "$E"

  # 검색 실행 → ID만 추출 → dedup
  # 머신 출력 모드로 ID만 받기 (UI 출력과의 맞물림 방지)
  FORMAT=ids "$SEARCH_SCRIPT" "$query" "$cat_field" "$pf_field" "$K" "1" 2>/dev/null \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' \
    | awk 'NF>0' \
    | LC_ALL=C sort -u > "$G" || true

  hits=$(comm -12 "$E" "$G" | wc -l | tr -d ' ')
  expected_count=$(wc -l < "$E" | tr -d ' ')
  # 분모는 항상 K (검색이 K개 미만이어도 분모 고정)
  precision=$(echo "scale=6; $hits / $K" | bc -l)

  # expected_count가 0인 경우 0으로 보호
  if [[ "$expected_count" -gt 0 ]]; then
    recall=$(echo "scale=6; $hits / $expected_count" | bc -l)
  else
    recall=0
  fi

  printf "%s\t%d\t%d\t%.4f\t%.4f\n" "$query" "$K" "$hits" "$precision" "$recall" | tee -a "$OUT" >/dev/null
  echo "  📊 ${query}: hits=${hits}, precision=$(printf '%.0f' "$(echo "$precision*100" | bc -l)")%, recall=$(printf '%.0f' "$(echo "$recall*100" | bc -l)")%"

  total_queries=$((total_queries+1))
  total_hits=$((total_hits+hits))
  total_expected=$((total_expected+expected_count))
  total_results=$((total_results+K))

  macro_p_sum=$(echo "scale=6; $macro_p_sum + $precision" | bc -l)
  macro_r_sum=$(echo "scale=6; $macro_r_sum + $recall" | bc -l)

  rm -f "$E" "$G"
  trap - RETURN
done < "$GT"

# 마이크로/매크로
if [[ "$total_results" -gt 0 ]]; then
  micro_p=$(echo "scale=6; $total_hits / $total_results" | bc -l)
else
  micro_p=0
fi
if [[ "$total_expected" -gt 0 ]]; then
  micro_r=$(echo "scale=6; $total_hits / $total_expected" | bc -l)
else
  micro_r=0
fi

if [[ "$total_queries" -gt 0 ]]; then
  macro_p=$(echo "scale=6; $macro_p_sum / $total_queries" | bc -l)
  macro_r=$(echo "scale=6; $macro_r_sum / $total_queries" | bc -l)
else
  macro_p=0; macro_r=0
fi

echo
printf "📈 최종 평가 결과:\n"
printf "  micro precision@%d = %.4f\n" "$K" "$micro_p"
printf "  micro recall@%d    = %.4f\n" "$K" "$micro_r"
printf "  macro precision@%d = %.4f\n" "$K" "$macro_p"
printf "  macro recall@%d    = %.4f\n" "$K" "$macro_r"
printf "\n📝 상세 결과 파일: %s\n" "$OUT"
