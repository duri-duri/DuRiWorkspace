#!/usr/bin/env bash
# Real Trace v2 benchmark runner (no dummy). Calls a concrete bench command and validates JSON.
set -Eeuo pipefail

# --- Arg parsing -------------------------------------------------------------
sampling="1.0"; ser="json"; comp="none"; out="out.json"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sampling) sampling="$2"; shift 2;;
    --ser|--serialization) ser="$2"; shift 2;;
    --comp|--compression) comp="$2"; shift 2;;
    --out) out="$2"; shift 2;;
    *) echo "[ERR] Unknown arg: $1" >&2; exit 2;;
  esac
done

# --- Resolve paths & command -------------------------------------------------
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
# No more fallback. Must be provided or installed on PATH.
BENCH_CMD="${TRACE_BENCH_CMD:-}"
TIMEOUT_SEC="${TRACE_BENCH_TIMEOUT:-120}"

if [[ -z "$BENCH_CMD" ]]; then
  # allow PATH lookup as a last resort if user explicitly wants it
  BENCH_CMD="$(command -v trace_bench || true)"
fi
if [[ -z "$BENCH_CMD" || ! -x "$BENCH_CMD" ]]; then
  echo "[ERR] TRACE_BENCH_CMD is not set and no 'trace_bench' found on PATH." >&2
  echo "      Export TRACE_BENCH_CMD to a real bench binary. No dummy allowed." >&2
  exit 2
fi

# --- REAL BENCH PROOF -------------------------------------------------------
# We require the bench to pass a self-check (or at least expose a version).
# Contract:
#   trace_bench --self-check  -> prints 'TRACE_BENCH_OK:<impl-id>'
#   or
#   trace_bench --version     -> prints non-empty version without '[BENCH]' or 'dummy'
if "$BENCH_CMD" --self-check 2>/dev/null | grep -q '^TRACE_BENCH_OK:' ; then
  : # ok
else
  VER="$("$BENCH_CMD" --version 2>/dev/null || true)"
  if [[ -z "$VER" ]] || echo "$VER" | grep -Eiq '(dummy|simulator|\[BENCH\])'; then
    echo "[ERR] Bench verification failed. Refusing to run with dummy/simulator." >&2
    echo "     Got version: '${VER:-<empty>}'" >&2
    exit 3
  fi
fi
# ---------------------------------------------------------------------------

# --- Flag mapping (keep consistent with bench binary) ------------------------
# Expected bench interface (example):
#   trace_bench --sampling <float> --serialization <json|msgpack|protobuf> \
#               --compression <none|gzip|zstd> --json-out <path>
json_out="${out}.tmp"
mkdir -p "$(dirname "$out")"

# --- Execute with timeout (if available) -------------------------------------
set +e
if command -v timeout >/dev/null 2>&1; then
  timeout --preserve-status "${TIMEOUT_SEC}" \
    "$BENCH_CMD" \
      --sampling "${sampling}" \
      --serialization "${ser}" \
      --compression "${comp}" \
      --json-out "${json_out}"
  rc=$?
else
  "$BENCH_CMD" \
      --sampling "${sampling}" \
      --serialization "${ser}" \
      --compression "${comp}" \
      --json-out "${json_out}"
  rc=$?
fi
set -e

if [[ $rc -ne 0 ]]; then
  echo "[ERR] Benchmark failed (rc=$rc) for sampling=${sampling}, ser=${ser}, comp=${comp}" >&2
  # Try to print last stderr log if the bench wrote it next to json (optional convention)
  if [[ -f "${json_out%.json}.stderr" ]]; then
    echo "--- bench stderr ---" >&2
    sed -n '1,200p' "${json_out%.json}.stderr" >&2 || true
    echo "--------------------" >&2
  fi
  exit $rc
fi

# --- Schema validation (no jq dependency; use Python stdlib) -----------------
python3 - "$json_out" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1])
try:
    d = json.loads(p.read_text(encoding="utf-8"))
except Exception as e:
    print(f"[ERR] Invalid JSON: {e}", file=sys.stderr); sys.exit(4)

def want(k, typ):
    if k not in d:
        print(f"[ERR] Missing key: {k}", file=sys.stderr); sys.exit(5)
    if not isinstance(d[k], (int,float)) and typ=="num":
        print(f"[ERR] Key {k} must be numeric", file=sys.stderr); sys.exit(6)

for k in ("p95_ms","error_rate","size_kb"):
    want(k,"num")

# Light sanity
if d["p95_ms"] <= 0: print("[ERR] p95_ms <= 0", file=sys.stderr); sys.exit(7)
if not (0 <= d["error_rate"] < 1): print("[ERR] error_rate out of [0,1)", file=sys.stderr); sys.exit(8)
if d["size_kb"] <= 0: print("[ERR] size_kb <= 0", file=sys.stderr); sys.exit(9)
PY

# --- Commit result atomically ------------------------------------------------
mv "${json_out}" "${out}"
echo "[OK] wrote ${out}"
