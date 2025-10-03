#!/usr/bin/env bash
set -Eeuo pipefail
command -v jq >/dev/null || { echo "[err] jq not found"; exit 2; }
export LC_ALL=C

# ---- defaults
K=50; RANK=0; FMT="pretty"; LOG_PATH=""; MODE="literal"
QUERY=""; CAT=""; PF=""; WEIGHTS="${WEIGHTS:-3,2,2,1}"

usage(){ cat <<'USAGE'
Usage:
  bash scripts/rag_search.sh "<query>" [--cat <category>] [--pf true|false]
                             [--rank] [--k N] [--format ids|json|pretty]
                             [--log <tsv-path>] [--mode literal|regex]
USAGE
}

# ---- (1) 쿼리(포지셔널) 먼저 흡수
if [[ $# -gt 0 && "$1" != --* ]]; then QUERY="$1"; shift; fi

# ---- (2) 옵션/포지셔널 혼재 허용
while [[ $# -gt 0 ]]; do
  case "$1" in
    --k)       K="${2:?--k requires N}"; shift 2;;
    --rank)    RANK=1; shift;;
    --format)  FMT="${2:?ids|json|pretty}"; shift 2;;
    --log)     LOG_PATH="${2:?--log requires path}"; shift 2;;
    --cat|--category) CAT="${2:?--cat requires value}"; shift 2;;
    --pf)      PF="${2:?--pf requires true|false}"; shift 2;;
    --mode)    MODE="${2:-literal}"; shift 2;;
    --help|-h) usage; exit 0;;
    --)        shift; break;;
    --*)       echo "[err] unknown option: $1" >&2; usage; exit 2;;
    *)         if   [[ -z "$CAT" ]]; then CAT="$1"
               elif [[ -z "$PF"  ]]; then PF="$1"
               else QUERY="${QUERY:+$QUERY }$1"
               fi
               shift;;
  esac
done
[[ -n "$QUERY" ]] || { usage; exit 1; }

# ---- (3) 검색 패턴(리터럴 기본) + 토큰 OR
ESC_Q="$QUERY"
if [[ "$MODE" == "literal" ]]; then
  ESC_Q="$(printf '%s' "$QUERY" | sed -E 's/([][(){}.^$|*+?\\])/\\\1/g')"
fi
RX="$(printf '%s' "$ESC_Q" | tr ' ' '\n' | awk '{if(length($0)){printf("%s%s",(NR>1?"|":""),$0)}}')"
[ -n "$RX" ] || RX="$ESC_Q"

# ---- (4) 가중치 파싱
TW=$(printf "%s" "$WEIGHTS" | cut -d, -f1)
GW=$(printf "%s" "$WEIGHTS" | cut -d, -f2)
BW=$(printf "%s" "$WEIGHTS" | cut -d, -f3)
DW=$(printf "%s" "$WEIGHTS" | cut -d, -f4)

# ---- (5) 데이터 로드 → 필터/스코어( jq 1.5 호환: splits 로 카운팅 )
TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
find rag/ -name '*.jsonl' -print0 \
| xargs -0 -I{} jq -c . {} 2>/dev/null \
| jq -c --arg rx "$RX" --arg cat "$CAT" --arg pf "$PF" \
       --argjson tw "$TW" --argjson gw "$GW" --argjson bw "$BW" --argjson dw "$DW" '
  . as $d
  | select(type=="object" and (has("title") and has("body")))
  | ( ($cat=="") or (.category==$cat) ) as $catok
  | ( ($pf=="")  or (.patient_facing==($pf=="true")) ) as $pfok
  | (($d.title // "")  | tostring | ascii_downcase)  as $t
  | (($d.body  // "")  | tostring | ascii_downcase)  as $b
  | ((($d.bullets // []) | join(" ") | tostring | ascii_downcase)) as $bul
  | ((($d.tags    // []) | join(" ") | tostring | ascii_downcase)) as $tg
  | ($t + " " + $b + " " + $bul + " " + $tg) as $all
  | ($all | test($rx; "i")) as $matched
  | select($catok and $pfok and $matched)
  | {
      id: ($d.id // "-"),
      title: ($d.title // ""),
      category: ($d.category // "-"),
      patient_facing: ($d.patient_facing // false),
      body: ($d.body // ""),
      _ct: (([ $t   | splits($rx) ] | length) - 1),
      _cg: (([ $tg  | splits($rx) ] | length) - 1),
      _cb: (([ $bul | splits($rx) ] | length) - 1),
      _cd: (([ $b   | splits($rx) ] | length) - 1)
    }
  | .score = (._ct*$tw + ._cg*$gw + ._cb*$bw + ._cd*$dw)
' > "$TMP"

# === replace: dedup + deterministic sort + topK (jq 1.5-safe) ===
RESULTS="$(mktemp)"; trap 'rm -f "$TMP" "$RESULTS"' EXIT
jq -rs --argjson k "$K" --argjson rank "$RANK" '
  # 1) id로 안정화 → id별 최고점만 남김
  sort_by(.id) | group_by(.id) | map(max_by(.score // 0)) |
  # 2) jq 1.5 호환: 배열키 정렬 대신 2-pass
  (if $rank==1
     then ( sort_by(.id) | sort_by(-(.score // 0)) )
     else   sort_by(.id)
   end) |
  .[:$k]
' "$TMP" > "$RESULTS"

# ---- (7) 출력
case "$FMT" in
  ids)   jq -r .[].id "$RESULTS";;
  json)  cat "$RESULTS";;
  pretty)
    jq -r '.[] | "📄 \(.id): \(.title)\n   카테고리: \(.category)\n   환자용: \(.patient_facing)\n   내용: \((.body|gsub("\n";" ")|.[0:160]))..."' "$RESULTS";;
  *) echo "[err] unknown format: $FMT" >&2; exit 2;;
esac

# ---- (8) 로그 (헤더 보장 + flock 있으면 잠금)
if [[ -n "$LOG_PATH" ]]; then
  mkdir -p "$(dirname "$LOG_PATH")"
  [[ -s "$LOG_PATH" ]] || printf "ts\tquery\tcat\tpf\tids\n" > "$LOG_PATH"
  ids_csv="$(jq -r '[.[].id] | join(",")' "$RESULTS")"
  ts="$(date --iso-8601=seconds 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
  if command -v flock >/dev/null 2>&1; then
    { flock -x 9; printf "%s\t%s\t%s\t%s\t%s\n" "$ts" "$QUERY" "$CAT" "$PF" "$ids_csv"; } 9>>"$LOG_PATH"
  else
    printf "%s\t%s\t%s\t%s\t%s\n" "$ts" "$QUERY" "$CAT" "$PF" "$ids_csv" >> "$LOG_PATH"
  fi
fi
