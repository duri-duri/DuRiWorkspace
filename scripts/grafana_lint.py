#!/usr/bin/env python3
import glob
import json
import sys

from jsonschema import ValidationError, validate

# Grafana 대시보드 스키마 (보강된 버전)
DASHBOARD_SCHEMA = {
    "type": "object",
    "required": ["title", "panels"],
    "properties": {
        "title": {"type": "string"},
        "schemaVersion": {"type": "number"},
        "uid": {"type": ["string", "null"]},
        "id": {"type": ["number", "null"]},
        "panels": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "targets"],
                "properties": {
                    "title": {"type": "string"},
                    "targets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["expr"],
                            "properties": {"expr": {"type": "string"}},
                        },
                    },
                },
            },
        },
    },
}


def validate_dashboard_json(file_path):
    """대시보드 JSON 스키마 검증"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # dashboard 래퍼가 있는 경우 내부 데이터 추출
        if "dashboard" in data:
            dashboard_data = data["dashboard"]
        else:
            dashboard_data = data

        validate(instance=dashboard_data, schema=DASHBOARD_SCHEMA)

        # 빈 expr 금지 검증
        panels = dashboard_data.get("panels", [])
        for panel in panels:
            if "targets" in panel:
                for target in panel["targets"]:
                    expr = target.get("expr", "")
                    if not str(expr).strip():
                        return False, "Empty PromQL expr in a panel target"

        return True, None
    except ValidationError as e:
        return False, f"Schema validation error: {e.message}"
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {e}"


def main():
    issues = []
    dashboard_files = glob.glob("grafana/**/*.json", recursive=True)

    for file_path in dashboard_files:
        # JSON 스키마 검증만 수행 (PromQL 검증은 제거)
        is_valid, error = validate_dashboard_json(file_path)
        if not is_valid:
            issues.append(f"{file_path}: {error}")

    if issues:
        for issue in issues:
            print(issue)
        sys.exit(1)
    else:
        print("All Grafana dashboards passed validation")


if __name__ == "__main__":
    main()
