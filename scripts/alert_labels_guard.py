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
REQ_IN_ANNOTATIONS = {
    "summary": re.compile(r"^\s*summary:\s*"),
    "description": re.compile(r"^\s*description:\s*"),
}


def check_file(path):
    missing = []
    with open(path, encoding="utf-8") as f:
        in_alert = False
        in_labels = False
        in_annotations = False
        have_labels = {k: False for k in REQ_IN_LABELS}
        have_annotations = {k: False for k in REQ_IN_ANNOTATIONS}

        def flush_block():
            nonlocal missing, have_labels, have_annotations, in_alert, in_labels, in_annotations
            if in_alert and not (all(have_labels.values()) and all(have_annotations.values())):
                missing.append(path)
            in_alert = False
            in_labels = False
            in_annotations = False
            have_labels = {k: False for k in REQ_IN_LABELS}
            have_annotations = {k: False for k in REQ_IN_ANNOTATIONS}

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
                in_annotations = True
                continue
            if in_alert and in_labels:
                for k, rx in REQ_IN_LABELS.items():
                    if rx.match(line):
                        have_labels[k] = True
            if in_alert and in_annotations:
                for k, rx in REQ_IN_ANNOTATIONS.items():
                    if rx.match(line):
                        have_annotations[k] = True
        # EOF 시 마지막 블록 평가
        flush_block()
    return missing


def main():
    fails = []
    for path in glob.glob("prometheus/rules/**/*.y*ml", recursive=True):
        fails += check_file(path)
    if fails:
        for f in sorted(set(fails)):
            print(f"MISSING labels or annotations in {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
