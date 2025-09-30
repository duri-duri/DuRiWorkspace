#!/usr/bin/env python3
import re, sys, json, pathlib, yaml

def load_rules(path="tools/failure_patterns.yml"):
    return yaml.safe_load(open(path))

def match_rules(log_text, rules):
    hits = []
    for r in rules.get("rules", []):
        if any(s in log_text for s in r.get("match", {}).get("any", [])):
            hits.append(r)
    return hits

def main():
    log = sys.stdin.read() if not sys.stdin.isatty() else ""
    rules = load_rules()
    hits = match_rules(log, rules)
    print(json.dumps({"matched_rules": [h["id"] for h in hits], "suggestions": [h["suggest"] for h in hits]}, indent=2))

if __name__ == "__main__":
    main()
