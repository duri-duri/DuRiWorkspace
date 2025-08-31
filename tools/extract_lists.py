#!/usr/bin/env python3
import sys, json, yaml
y = yaml.safe_load(open(sys.argv[1], 'r', encoding='utf-8'))

# 필수/허용 키
allowed = {"version","whitelist","blacklist","budgets","notes","canary","gates","plan_max_files"}
unknown = set(y.keys()) - allowed if isinstance(y, dict) else set()
if unknown:
    print(f"[FAIL] unknown keys in policy: {sorted(unknown)}", file=sys.stderr)
    sys.exit(2)

if not isinstance(y.get("whitelist", []), list) or not isinstance(y.get("blacklist", []), list):
    print("[FAIL] whitelist/blacklist must be lists", file=sys.stderr)
    sys.exit(2)

def norm(xs): return [str(s).lstrip("./") for s in (xs or [])]
print(json.dumps({"whitelist": norm(y.get("whitelist")),
                  "blacklist": norm(y.get("blacklist")),
                  "version": y.get("version", 1)}, ensure_ascii=False))
