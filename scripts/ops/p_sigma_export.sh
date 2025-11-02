#!/usr/bin/env bash
# B. p-분산 메트릭 안전 모드로 교체(없으면 0, 있으면 표준편차 산출)
set -euo pipefail

cd "$(dirname "$0")/.."

: "${TEXTFILE_DIR:=.reports/synth}"
out="$TEXTFILE_DIR/p_sigma.prom"

# p_values_2h.prom, p_values_24h.prom에서 p-value 수집
p_list=""

for f in "$TEXTFILE_DIR/p_values_2h.prom" "$TEXTFILE_DIR/p_values_24h.prom"; do
    if [ -f "$f" ]; then
        p_list+=$(awk '/^p_value/ {print $2" "}' "$f" 2>/dev/null || true)
    fi
done

if [ -z "$p_list" ]; then
    {
        echo "# HELP duri_p_sigma p-value stddev (fallback=NaN)"
        echo "# TYPE duri_p_sigma gauge"
        echo "duri_p_sigma NaN"
    } > "$out"
    exit 0
fi

# 표준편차 계산
read -ra vals <<< "$p_list"
n=${#vals[@]}

if [ "$n" -eq 0 ]; then
    {
        echo "# HELP duri_p_sigma p-value stddev (fallback=NaN)"
        echo "# TYPE duri_p_sigma gauge"
        echo "duri_p_sigma NaN"
    } > "$out"
    exit 0
fi

# 합 계산
sum=0
for x in "${vals[@]}"; do
    sum=$(python3 -c "print($sum + float('$x'))" 2>/dev/null || echo "$sum")
done

# 평균 계산
mean=$(python3 -c "print($sum / $n)" 2>/dev/null || echo "0")

# 분산 계산
sq=0
for x in "${vals[@]}"; do
    diff=$(python3 -c "print(float('$x') - $mean)" 2>/dev/null || echo "0")
    sq=$(python3 -c "print($sq + ($diff)**2)" 2>/dev/null || echo "$sq")
done

# 표준편차 계산
sigma=$(python3 -c "import math; print(math.sqrt($sq / max($n-1,1)))" 2>/dev/null || echo "0")

{
    echo "# HELP duri_p_sigma p-value stddev"
    echo "# TYPE duri_p_sigma gauge"
    echo "duri_p_sigma $sigma"
} > "$out"

echo "[OK] p-value sigma exported: $sigma (n=$n)"
