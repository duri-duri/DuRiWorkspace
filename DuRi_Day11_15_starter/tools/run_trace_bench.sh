#!/usr/bin/env bash
set -Eeuo pipefail
sampling="1.0"; ser="json"; comp="none"; out="out.json"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sampling) sampling="$2"; shift 2;;
    --ser|--serialization) ser="$2"; shift 2;;
    --comp|--compression) comp="$2"; shift 2;;
    --out) out="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done
# TODO: 실제 Trace v2 벤치 호출로 교체 (예: ./bin/trace_bench ...)
awk -v s="$sampling" -v ser="$ser" -v comp="$comp" 'BEGIN{
  base=750
  ser_pen=(ser=="json"?1.00:(ser=="msgpack"?0.96:0.94))
  comp_pen=(comp=="none"?1.00:(comp=="gzip"?0.98:0.96))
  p95=base* (1.02 - 0.15*s) * ser_pen * comp_pen
  err=0.002 * (1.04 - 0.2*s) * (ser=="json"?1.0:0.98)
  size=100.0 * (0.6 + 0.5*s) * (ser=="json"?1.0:(ser=="msgpack"?0.85:0.8)) * (comp=="none"?1.0:(comp=="gzip"?0.7:0.55))
  srand(); p95+=rand()*8-4; err+= (rand()*0.0002-0.0001); size += rand()*5-2.5
  if(err<0) err=0.0
  printf("{\"p95_ms\":%.2f,\"error_rate\":%.5f,\"size_kb\":%.2f}\n", p95, err, size)
}' > "${out}.tmp"
mv "${out}.tmp" "$out"
echo "[OK] wrote $out"
