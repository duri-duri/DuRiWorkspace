#!/usr/bin/env bash
set -euo pipefail
#
# Grafana에 주석(Annotation)을 남깁니다.
# 사용법:
#   export GRAFANA_URL="http://localhost:3000"
#   export GRAFANA_TOKEN="****"     # Grafana API token (Editor 이상)
#   tools/annotate_grafana.sh -t "Canary start" -g "duri,canary" -d "<DASHBOARD_UID>"
# 선택 옵션:
#   -p <panel_id>         특정 패널에만 주석 연결 (미지정 시 전체 대시보드)
#   -m <epoch_ms>         주석 시각(밀리초). 기본값: 현재 시각
#

usage() {
  cat <<'USAGE'
Usage:
  annotate_grafana.sh -t "<text>" [-g "tag1,tag2"] [-d <dashboard_uid>] [-p <panel_id>] [-m <epoch_ms>]

Env:
  GRAFANA_URL   (예: http://localhost:3000)
  GRAFANA_TOKEN (Grafana API Token)
USAGE
}

TEXT=""
TAGS="duri,canary"
DASH_UID=""
PANEL_ID=""
TIME_MS=""

while getopts ":t:g:d:p:m:h" opt; do
  case "$opt" in
    t) TEXT="$OPTARG" ;;
    g) TAGS="$OPTARG" ;;
    d) DASH_UID="$OPTARG" ;;
    p) PANEL_ID="$OPTARG" ;;
    m) TIME_MS="$OPTARG" ;;
    h) usage; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2; usage; exit 2 ;;
    :) echo "Option -$OPTARG requires an argument." >&2; usage; exit 2 ;;
  esac
done

if [[ -z "${GRAFANA_URL:-}" || -z "${GRAFANA_TOKEN:-}" ]]; then
  echo "ERROR: GRAFANA_URL/GRAFANA_TOKEN 환경변수가 필요합니다." >&2
  exit 2
fi
if [[ -z "$TEXT" ]]; then
  echo "ERROR: -t <text> 는 필수입니다." >&2
  exit 2
fi

# now(밀리초)
if [[ -z "$TIME_MS" ]]; then
  if date +%s%3N >/dev/null 2>&1; then
    TIME_MS="$(date +%s%3N)"
  else
    TIME_MS="$(( $(date +%s) * 1000 ))"
  fi
fi

# JSON 조립
IFS=',' read -r -a TAG_ARR <<< "$TAGS"
TAGS_JSON=$(printf '"%s",' "${TAG_ARR[@]}"); TAGS_JSON="[${TAGS_JSON%,}]"

payload='{"text":'"$(jq -Rn --arg t "$TEXT" '$t')"',"time":'"$TIME_MS"',"tags":'"$TAGS_JSON"'}'
if [[ -n "$DASH_UID" ]]; then
  payload=$(jq -cn --argjson base "$payload" --arg d "$DASH_UID" '$base + {dashboardUID:$d}')
fi
if [[ -n "$PANEL_ID" ]]; then
  payload=$(jq -cn --argjson base "$payload" --argjson p "$PANEL_ID" '$base + {panelId:$p}')
fi

curl -sS -X POST \
  -H "Authorization: Bearer ${GRAFANA_TOKEN}" \
  -H 'Content-Type: application/json' \
  --data "$payload" \
  "${GRAFANA_URL%/}/api/annotations" | jq .

echo "✅ Grafana annotation created at ${TIME_MS}ms"


















