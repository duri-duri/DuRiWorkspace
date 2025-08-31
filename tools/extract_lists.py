#!/usr/bin/env python3
import sys, json, yaml
y = yaml.safe_load(open(sys.argv[1], 'r', encoding='utf-8'))
def norm(xs): return [str(s).lstrip("./") for s in (xs or [])]
print(json.dumps({"whitelist": norm(y.get("whitelist")),
                  "blacklist": norm(y.get("blacklist")),
                  "version": y.get("version", 1)}, ensure_ascii=False))
