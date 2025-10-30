#!/usr/bin/env python3
import sys, csv, math
from statistics import mean, pstdev

def load(path):
    xs=[]
    try:
        with open(path, newline='') as f:
            for row in csv.reader(f):
                if row and row[0].strip():
                    try: xs.append(float(row[0]))
                    except: pass
    except FileNotFoundError:
        pass
    return xs

A=load('data/A.csv'); B=load('data/B.csv')
if len(A)<2 or len(B)<2:
    print("1"); sys.exit(0)
ma, mb = mean(A), mean(B)
sa, sb = pstdev(A) or 1e-9, pstdev(B) or 1e-9
na, nb = len(A), len(B)
t = (ma-mb) / math.sqrt(sa*sa/na + sb*sb/nb)
df = (sa*sa/na + sb*sb/nb)**2 / ((sa*sa/na)**2/(na-1) + (sb*sb/nb)**2/(nb-1))
try:
    import scipy.stats as ss
    p = float(ss.t.sf(abs(t), df)*2)
except Exception:
    try:
        import mpmath as mp
        p = float(2*(1-mp.ncdf(abs(t))))
    except Exception:
        p = 1.0
print(p)
