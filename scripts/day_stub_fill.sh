#!/usr/bin/env bash
set -euo pipefail
scan=".reports/day_status_40_60.tsv"
tmpl_rep="DuRi_Day11_15_starter/DAY%02d_COMPLETION_REPORT.md"
tmpl_ver="DuRi_Day11_15_starter/verify_out/day_%d.json"

while read -r line; do
  [[ "$line" =~ ^day ]] && continue
  d=$(echo "$line" | awk '{print $1}')
  rep=$(echo "$line" | awk '{print $4}')
  vjs=$(echo "$line" | awk '{print $5}')

  if [[ -z "$rep" ]]; then
    f=$(printf "$tmpl_rep" "$d")
    mkdir -p "$(dirname "$f")"
    cat > "$f" <<EOF
# DAY ${d} COMPLETION REPORT

## Scope
- (간단히 범위 기입)

## Evidence
- CI status: (링크/로그 요약)
- Prometheus rules: (해당 시점 적용 여부)
- RAG/WF: (관련 이슈/커밋)

## Status
- [ ] Complete (증빙 보강 필요)
- 작성일: 2025-10-13 KST
EOF
  fi

  if [[ -z "$vjs" ]]; then
    f2=$(printf "$tmpl_ver" "$d")
    mkdir -p "$(dirname "$f2")"
    echo '{"status":"stub","note":"to be backfilled","generated_at":"2025-10-13T09:00:00+09:00"}' > "$f2"
  fi
done < "$scan"

git add DuRi_Day11_15_starter/DAY*_COMPLETION_REPORT.md DuRi_Day11_15_starter/verify_out/day_*.json
git commit -m "Phase2 gap fill: Day40–60 stub completion reports + verify_out placeholders (2025-10-13 KST)"
