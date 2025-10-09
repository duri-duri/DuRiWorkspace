#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$(readlink -f "$0")")/../lib/loop_common.sh"

REPO_ROOT="$(repo_root)"
cd "$REPO_ROOT"   # ✅ 항상 루트부터 시작

# ---------------- args & defaults ----------------
IN="${1:-$REPO_ROOT/.reports/metrics/day66_metrics.tsv}"
K="${2:-${METRIC_K:-3}}"

# ---------------- preserve CLI overrides (highest priority) ----------------
CLI_TH_NDCG="${TH_NDCG-}"
CLI_TH_MRR="${TH_MRR-}"
CLI_TH_ORACLE="${TH_ORACLE-}"
CLI_GUARD_STRICT="${GUARD_STRICT-}"
CLI_STRICT_EXIT_CODE="${STRICT_EXIT_CODE-}"

# ---------------- load envs (as defaults) ----------------
[[ -r "$REPO_ROOT/.reports/metrics/day66_thresholds.env" ]] && source "$REPO_ROOT/.reports/metrics/day66_thresholds.env"
[[ -r "/etc/default/duri-workspace" ]] && source "/etc/default/duri-workspace" 2>/dev/null || true

# ---------------- re-apply CLI overrides ----------------
[[ -n "${CLI_TH_NDCG}"        ]] && TH_NDCG="$CLI_TH_NDCG"
[[ -n "${CLI_TH_MRR}"         ]] && TH_MRR="$CLI_TH_MRR"
[[ -n "${CLI_TH_ORACLE}"      ]] && TH_ORACLE="$CLI_TH_ORACLE"
[[ -n "${CLI_GUARD_STRICT}"   ]] && GUARD_STRICT="$CLI_GUARD_STRICT"
[[ -n "${CLI_STRICT_EXIT_CODE}" ]] && STRICT_EXIT_CODE="$CLI_STRICT_EXIT_CODE"

GUARD_STRICT="${GUARD_STRICT:-0}"       # 1=회귀시 실패코드로 종료, 0=로그만
STRICT_EXIT_CODE="${STRICT_EXIT_CODE:-2}"

log() {
  if command -v logger >/dev/null 2>&1; then
    logger -t duri-alert "$*"
  else
    echo "$*"
  fi
}

# ---------------- input checks ----------------
parse_error=0
read_header="$(head -1 "$IN" 2>/dev/null || true)"
if [[ -z "$read_header" ]]; then
  log "[guard] no metrics file: $IN"
  parse_error=1
fi

# ---------------- parse overall line robustly (TSV) ----------------
# 기대 스키마: scope  domain  count  ndcg@K  mrr  oracle_recall@K
# 첫 컬럼이 'all'인 줄을 정확히 집계
if [[ -f "$IN" ]]; then
  overall_line="$(awk -F'\t' 'NR>1 && $1=="all"{print; exit}' "$IN" || true)"
  if [[ -z "$overall_line" ]]; then
    log "[guard] no overall line in $IN"
    parse_error=1
  fi
else
  log "[guard] file not found: $IN"
  parse_error=1
fi

if [[ $parse_error -eq 0 ]]; then
  ndcg="$(awk -F'\t' '{print $4}' <<<"$overall_line")"
  mrr="$(awk  -F'\t' '{print $5}' <<<"$overall_line")"
  oracle="$(awk -F'\t' '{print $6}' <<<"$overall_line")"
fi

# ---------------- comparisons ----------------
# awk의 비교식은 올바르게 quoting하면 안전합니다.
pass=1
if [[ $parse_error -eq 0 ]]; then
  awk -v n="$ndcg"  -v th="${TH_NDCG:-0.0}"  'BEGIN{exit !(n>=th)}' || pass=0
  awk -v n="$mrr"   -v th="${TH_MRR:-0.0}"   'BEGIN{exit !(n>=th)}' || pass=0
  awk -v n="$oracle" -v th="${TH_ORACLE:-0.0}" 'BEGIN{exit !(n>=th)}' || pass=0
fi

# ... 비교 끝난 뒤
if (( parse_error == 1 )); then
  log "[guard] parse error, file=$IN"
  exit 1
fi

if (( pass==1 )); then
  log "[guard] OK ndcg@${K}=${ndcg} mrr=${mrr} oracle@${K}=${oracle}"
  echo "GUARD_RESULT=ok K=${K} ndcg=${ndcg} mrr=${mrr} oracle=${oracle}"
  exit 0
else
  >&2 echo "[guard] REGRESSION ndcg@${K}=${ndcg} mrr=${mrr} oracle@${K}=${oracle} (th ${TH_NDCG}/${TH_MRR}/${TH_ORACLE})"
  echo "GUARD_RESULT=regression K=${K} ndcg=${ndcg} mrr=${mrr} oracle=${oracle}"
  if [[ "${GUARD_STRICT:-0}" == "1" ]]; then
    exit 2
  else
    exit 0
  fi
fi
