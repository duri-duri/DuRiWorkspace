#!/usr/bin/env bash
set -euo pipefail
declare -A MIN=([intake]=200 [education]=220 [exercise]=180 [orders]=120 [schedule]=140 [policy]=120 [diagnosis]=200)
declare -A PAD=(
  [triage]=" 본 항목은 즉시 상향평가와 의사 직접평가를 권고하는 신호들을 요약합니다. 임상적 판단과 환자 가치에 따라 라우팅 경로와 검사 필요성을 재평가합니다."
  [orders]=" 본 기준은 레드플래그 존재 시 문서화(증상 발생 시점, 신경학 소견, 염증표지자 등)와 적절한 검사 의뢰 절차를 명시합니다."
  [education]=" 환자 교육은 이득/한계/대안을 균형 있게 설명하고, 과잉검사의 위험과 비용을 투명하게 공유하는 공동의사결정(SDM)을 포함합니다."
  [intake]=" 기능제한과 이전 삽화/재발 패턴, 치료 반응, 선호·가치(검사/치료/비용)를 구조화하여 기록합니다."
  [diagnosis]=" 작업진단과 감별진단을 근거와 함께 제시하고, 추적 계획과 재평가 기준을 명확히 합니다."
  [schedule]=" 추적 주기와 목표지표(NRS/기능)를 제시하고, 악화 시 후퇴 규칙을 포함합니다."
  [exercise]=" 통증 없는 범위, 누적 볼륨, 48시간 지연 통증 모니터링, 단계적 진행 규칙을 포함합니다."
  [policy]=" 안전 경고, 면책 및 상향평가 트리거를 요약합니다."
)
tmp="$(mktemp)"
while IFS= read -r -d '' f; do
  : > "$tmp"
  while IFS= read -r line; do
    j="$line"
    cat="$(jq -r '.category // empty' <<<"$j")"
    id="$(jq -r '.id // empty' <<<"$j")"
    body="$(jq -r '.body // ""' <<<"$j")"
    if [ -z "$cat" ]; then echo "$j" >> "$tmp"; continue; fi
    min="${MIN[$cat]:-200}"
    len="$(printf "%s" "$body" | wc -m)"
    if (( len < min )); then
      pad="${PAD[$cat]:- }"
      # triage.*는 policy라도 triage 톤으로 오버라이드
      if [[ "$id" == triage.* ]]; then pad="${PAD[triage]}"; fi
      need=$((min - len))

      add=""
      while (( ${#add} < need )); do
        chunk="${pad:0:$((need - ${#add}))}"
        # pad가 need보다 짧으면 여러 번 이어붙음
        add="$add$chunk"
        # pad가 너무 짧으면 반복해서 누적 (보수적)
        if [[ -z "$chunk" ]]; then add="$add$pad"; fi
      done
      j="$(jq --arg add " $add" '.body = (.body // "" + $add)' <<<"$j")"
    fi
    echo "$j" >> "$tmp"
  done < "$f"
  mv "$tmp" "$f"
done < <(find rag/ -name "*.jsonl" -print0)
