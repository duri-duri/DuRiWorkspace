#!/usr/bin/env python3
import json
import sys

import yaml


def flatten(xs):
    out = []
    if xs is None:
        return out
    for x in xs:
        if isinstance(x, (list, tuple)):
            out.extend(flatten(x))
        else:
            out.append(x)
    return out


y = yaml.safe_load(open(sys.argv[1], "r", encoding="utf-8"))
# allow extra keys but ignore them here; schema check는 쉘에서 수행하거나 별도 경고만
wl_raw = flatten(y.get("whitelist"))
bl_raw = flatten(y.get("blacklist"))


def norm(seq):
    if not seq:
        return []
    return [str(s).lstrip("./") for s in seq]


out = {
    "whitelist": norm(wl_raw),
    "blacklist": norm(bl_raw),
    "version": y.get("version", 1),
}
print(json.dumps(out, ensure_ascii=False))
