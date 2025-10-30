#!/usr/bin/env python3
import os, time, math, json, pathlib
out = pathlib.Path('var/metrics/ab_eval.prom'); out.parent.mkdir(parents=True, exist_ok=True)
p = None
src_json = pathlib.Path('var/metrics/ab_eval.json')
if src_json.exists():
    try:
        dat = json.loads(src_json.read_text())
        A, B = dat.get('groupA',{}), dat.get('groupB',{})
        if all(k in A for k in ('n','mean','var')) and all(k in B for k in ('n','mean','var')):
            na, nb = max(1,int(A['n'])), max(1,int(B['n']))
            ma, mb = float(A['mean']), float(B['mean'])
            va, vb = max(1e-9,float(A['var'])), max(1e-9,float(B['var']))
            t = (ma-mb)/((va/na + vb/nb)**0.5)
            from math import erf, sqrt
            def ncdf(x): return 0.5*(1+erf(x/sqrt(2)))
            p = 2*(1-ncdf(abs(t)))
    except Exception:
        p = None
ts = int(time.time())
lines = [
    '# HELP duri_ab_p_value AB evaluation p-value (lower is better).',
    '# TYPE duri_ab_p_value gauge',
    f'duri_ab_p_value {{source="auto"}} {p if (p is not None and math.isfinite(p)) else -1.0} {ts}000'
]
open(out,'w').write('\n'.join(lines)+'\n')
print('wrote', out)
