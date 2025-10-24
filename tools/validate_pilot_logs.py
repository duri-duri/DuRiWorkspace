#!/usr/bin/env python3
"""
Day41~43: PoU Pilot Log Schema Validator
기존 로깅 시스템과 호환되는 스키마 검증
"""

import argparse
import json
import sys
from pathlib import Path

import jsonschema


def validate_log_file(log_file: str, schema_file: str) -> bool:
    """로그 파일의 스키마 검증"""

    # 스키마 로드
    with open(schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # 로그 파일 검증
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        entry = json.loads(line.strip())
                        jsonschema.validate(entry, schema)
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error at line {line_num}: {e}")
                        return False
                    except jsonschema.ValidationError as e:
                        print(f"❌ Schema validation error at line {line_num}: {e.message}")
                        return False

        print(f"✅ Schema validation passed for {log_file}")
        return True

    except FileNotFoundError:
        print(f"❌ Log file not found: {log_file}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="PoU Pilot Log Schema Validator")
    parser.add_argument("--log-file", required=True, help="Log file to validate")
    parser.add_argument(
        "--schema-file",
        default="schemas/pilot_log_schema.json",
        help="Schema file path",
    )

    args = parser.parse_args()

    if not Path(args.schema_file).exists():
        print(f"❌ Schema file not found: {args.schema_file}")
        sys.exit(1)

    success = validate_log_file(args.log_file, args.schema_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
