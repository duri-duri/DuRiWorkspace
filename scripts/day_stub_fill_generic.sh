#!/usr/bin/env bash
set -euo pipefail
scan="${1:?usage: scan_tsv}"
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
# DAY $(printf "%02d" "$d") COMPLETION REPORT

## Scope
- (간단히 범위 기입)

## Evidence
- CI status: (pytest 통과 로그 요약)
- Prometheus rules: (해당 시점 적용 여부)
- RAG/WF: (관련 커밋/태그)

## Status
- [ ] Complete (증빙 보강 필요)
- 작성일: $(date +'%Y-%m-%d %H:%M KST')
EOF
  fi
  if [[ -z "$vjs" ]]; then
    f2=$(printf "$tmpl_ver" "$d")
    mkdir -p "$(dirname "$f2")"
    echo '{"status":"stub","note":"to be backfilled","generated_at":"'"$(date -Is)"'"}' > "$f2"
  fi
done < "$scan"
git add DuRi_Day11_15_starter/DAY*_COMPLETION_REPORT.md DuRi_Day11_15_starter/verify_out/day_*.json || true
git commit -m "Phase1 gap fill: Day01–30 stub completion reports + verify_out placeholders ($(date +'%Y-%m-%d KST'))" || true
