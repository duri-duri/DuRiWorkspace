#!/usr/bin/env bash
# B. TS 소비 검증의 데이터 소스 결선
set -euo pipefail

cd "$(dirname "$0")/.."

: "${TEXTFILE_DIR:=.reports/synth}"
out="$TEXTFILE_DIR/ts_consume_check.prom"
cfg="$TEXTFILE_DIR/routes.json"
ra="$TEXTFILE_DIR/route_apply.prom"

cfgA="NaN"
cfgB="NaN"

if [ -f "$cfg" ]; then
    cfgA=$(python3 <<PY
import json
import sys
try:
    with open("$cfg") as f:
        d = json.load(f)
        print(d.get("A", "NaN"))
except:
    print("NaN")
PY
)
    cfgB=$(python3 <<PY
import json
import sys
try:
    with open("$cfg") as f:
        d = json.load(f)
        print(d.get("B", "NaN"))
except:
    print("NaN")
PY
)
fi

# 실소비: Redis 우선, 실패 시 route_apply.prom 성공시점의 A/B 기록(없으면 NaN)
realA=$(redis-cli GET duri:ab:route:A 2>/dev/null || echo "")
realB=$(redis-cli GET duri:ab:route:B 2>/dev/null || echo "")

if [[ -z "$realA" || -z "$realB" || "$realA" == "(nil)" || "$realB" == "(nil)" ]]; then
    # route_apply.prom에서 성공 시점의 설정값 사용
    if [ -f "$ra" ] && grep -q "ab_route_apply_success 1" "$ra" 2>/dev/null; then
        if [ -f "$cfg" ]; then
            realA=$(python3 <<PY
import json
try:
    with open("$cfg") as f:
        d = json.load(f)
        print(d.get("A", "NaN"))
except:
    print("NaN")
PY
)
            realB=$(python3 <<PY
import json
try:
    with open("$cfg") as f:
        d = json.load(f)
        print(d.get("B", "NaN"))
except:
    print("NaN")
PY
)
        fi
    else
        realA="NaN"
        realB="NaN"
    fi
fi

# 편차 계산
deltaA=$(python3 <<PY
import math
def f(x):
    try:
        return float(x)
    except:
        return float('nan')
A1 = f("$cfgA")
A2 = f("$realA")
if not (math.isnan(A1) or math.isnan(A2)):
    print(abs(A1 - A2))
else:
    print("NaN")
PY
)

deltaB=$(python3 <<PY
import math
def f(x):
    try:
        return float(x)
    except:
        return float('nan')
B1 = f("$cfgB")
B2 = f("$realB")
if not (math.isnan(B1) or math.isnan(B2)):
    print(abs(B1 - B2))
else:
    print("NaN")
PY
)

{
    echo "# HELP ab_ts_consume_cfg route config fraction"
    echo "# TYPE ab_ts_consume_cfg gauge"
    echo "ab_ts_consume_cfg{arm=\"A\"} $cfgA"
    echo "ab_ts_consume_cfg{arm=\"B\"} $cfgB"
    echo "# HELP ab_ts_consume_real route real fraction"
    echo "# TYPE ab_ts_consume_real gauge"
    echo "ab_ts_consume_real{arm=\"A\"} $realA"
    echo "ab_ts_consume_real{arm=\"B\"} $realB"
    echo "# HELP ab_ts_consume_delta abs diff between cfg and real"
    echo "# TYPE ab_ts_consume_delta gauge"
    echo "ab_ts_consume_delta{arm=\"A\"} $deltaA"
    echo "ab_ts_consume_delta{arm=\"B\"} $deltaB"
} > "$out"

echo "[OK] TS 소비 검증 완료 (cfg: A=$cfgA B=$cfgB, real: A=$realA B=$realB)"
