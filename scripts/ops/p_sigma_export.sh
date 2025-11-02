#!/usr/bin/env bash
set -euo pipefail

# --- 1) 루트/경로 고정 ---
ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
TEXTFILE_DIR="${TEXTFILE_DIR:-"$ROOT/.reports/synth"}"
OUT="$TEXTFILE_DIR/p_sigma.prom"
P2H="$TEXTFILE_DIR/p_values_2h.prom"
P24H="$TEXTFILE_DIR/p_values_24h.prom"

mkdir -p "$TEXTFILE_DIR"

# --- 2) p 값 수집 ---
vals=""
for f in "$P2H" "$P24H"; do
  [[ -f "$f" ]] && vals+=$(awk '/^p_value/ {printf "%s ", $2}' "$f")
done

# --- 3) sigma 계산 ---
sigma="NaN"; n="0"
if [[ -n "${vals// /}" ]]; then
  # 파이프 없이 안전 계산
  read -r sigma n <<EOF
$(python3 - <<'PY'
import math, sys
data = [float(x) for x in sys.stdin.read().strip().split()]
if not data:
    print("NaN 0")
else:
    n = len(data)
    m = sum(data)/n
    var = sum((x-m)**2 for x in data)/max(n-1,1)
    print(f"{math.sqrt(var):.10f} {n}")
PY
<<<"${vals}")
EOF
fi

# --- 4) 파일에 '반드시' 씀(단일 리다이렉션 블록) ---
{
  echo "# HELP duri_p_sigma p-value stddev"
  echo "# TYPE duri_p_sigma gauge"
  echo "duri_p_sigma ${sigma}"
  echo "# HELP duri_p_sigma_samples number of p-values aggregated"
  echo "# TYPE duri_p_sigma_samples gauge"
  echo "duri_p_sigma_samples ${n}"
} > "$OUT"

echo "[OK] p-value sigma exported: ${sigma} (n=${n}) -> $OUT"
