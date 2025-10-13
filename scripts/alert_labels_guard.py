#!/usr/bin/env python3
import glob
import re
import sys

ALERT_RE = re.compile(r"^\s*-\s*alert:\s*")
LABELS_OPEN_RE = re.compile(r"^\s*labels:\s*$")
ANNOT_OPEN_RE = re.compile(r"^\s*annotations:\s*$")
REQ_IN_LABELS = {
    "severity": re.compile(r"^\s*severity:\s*"),
    "team": re.compile(r"^\s*team:\s*"),
    "runbook_url": re.compile(r"^\s*runbook_url:\s*"),
}


def check_file(path):
    missing = []
    with open(path, encoding="utf-8") as f:
        in_alert = False
        in_labels = False
        have = {k: False for k in REQ_IN_LABELS}

        def flush_block():
            nonlocal missing, have, in_alert, in_labels
            if in_alert and not all(have.values()):
                missing.append(path)
            in_alert = False
            in_labels = False
            have = {k: False for k in REQ_IN_LABELS}

        for line in f:
            if ALERT_RE.match(line):
                flush_block()
                in_alert = True
                continue
            if in_alert and LABELS_OPEN_RE.match(line):
                in_labels = True
                continue
            if in_alert and ANNOT_OPEN_RE.match(line):
                in_labels = False
                continue
            if in_alert and in_labels:
                for k, rx in REQ_IN_LABELS.items():
                    if rx.match(line):
                        have[k] = True
        # EOF 시 마지막 블록 평가
        flush_block()
    return missing


def main():
    fails = []
    for path in glob.glob("prometheus/rules/**/*.y*ml", recursive=True):
        fails += check_file(path)
    if fails:
        for f in sorted(set(fails)):
            print(f"MISSING labels in {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
