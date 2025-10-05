#!/usr/bin/env python3
import json
import pathlib
import re
import sys

import yaml


def load_rules(path="tools/failure_patterns.yml"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if "rules" not in data:
            data["rules"] = []
        return data
    except Exception as e:
        return {"rules": []}


def match_rules(log_text, rules):
    hits = []
    for r in rules.get("rules", []):
        if any(s in log_text for s in r.get("match", {}).get("any", [])):
            # Add confidence score to each hit
            hit = r.copy()
            hit["confidence"] = r.get("confidence", 0.5)
            hits.append(hit)
    return hits


def main():
    log = sys.stdin.read() if not sys.stdin.isatty() else ""
    rules = load_rules()
    hits = match_rules(log, rules)

    # Enhanced output with confidence scores and rule IDs
    # 테스트가 기대하는 형식: matched_rules는 문자열 ID 리스트
    matched_rule_ids = [h["id"] for h in hits]
    result = {
        "matched_rules": matched_rule_ids,  # 문자열 ID 리스트로 변경
        "suggestions": [h["suggest"] for h in hits],
        "total_matches": len(hits),
        "avg_confidence": sum(h["confidence"] for h in hits) / len(hits) if hits else 0,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
