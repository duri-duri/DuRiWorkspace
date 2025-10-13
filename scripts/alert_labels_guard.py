#!/usr/bin/env python3
import re, glob, sys
fail = 0
pat = re.compile(r'^\s*-\s*alert:\s*')
label_pat = re.compile(r'^\s*(severity|team|runbook_url):\s*')

for f in glob.glob('prometheus/rules/*.y*ml'):
    in_alert = False
    sev = team = rb = False
    with open(f, encoding='utf-8') as file:
        for line in file:
            if pat.match(line):
                if in_alert and not (sev and team and rb):
                    print(f"MISSING labels in {f}")
                    fail = 1
                in_alert = True
                sev = team = rb = False
            elif in_alert and label_pat.match(line):
                key = label_pat.match(line).group(1)
                if key == 'severity': sev = True
                elif key == 'team': team = True
                elif key == 'runbook_url': rb = True
        if in_alert and not (sev and team and rb):
            print(f"MISSING labels in {f}")
            fail = 1

sys.exit(fail)
