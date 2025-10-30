#!/usr/bin/env python3
# Minimal AB p-value generator: standardized Prometheus text without labels/timestamps
import math, json, pathlib

out = pathlib.Path('var/metrics/ab_eval.prom')
out.parent.mkdir(parents=True, exist_ok=True)

p = None
src_json = pathlib.Path('var/metrics/ab_eval.json')
if src_json.exists():
	try:
		dat = json.loads(src_json.read_text())
		A, B = dat.get('groupA', {}), dat.get('groupB', {})
		if all(k in A for k in ('n', 'mean', 'var')) and all(k in B for k in ('n', 'mean', 'var')):
			na, nb = max(1, int(A['n'])), max(1, int(B['n']))
			ma, mb = float(A['mean']), float(B['mean'])
			va, vb = max(1e-9, float(A['var'])), max(1e-9, float(B['var']))
			t = (ma - mb) / ((va/na + vb/nb) ** 0.5)
			from math import erf, sqrt
			def ncdf(x):
				return 0.5 * (1 + erf(x / sqrt(2)))
			p = 2 * (1 - ncdf(abs(t)))
	except Exception:
		p = None

val = p if (p is not None and math.isfinite(p)) else float('nan')
value_str = 'NaN' if math.isnan(val) else ('{:.12g}'.format(val))
text = (
	'# HELP duri_ab_p_value Two-tailed p-value from AB eval\n'
	'# TYPE duri_ab_p_value gauge\n'
	'duri_ab_p_value ' + value_str + '\n'
)
out.write_text(text)
print('wrote', out)
