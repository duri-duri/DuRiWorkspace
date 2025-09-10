#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
failure_to_goal_adapter.py
Input: test_result.json (기존 존재)
Output: test_result_for_goals.json (error_to_goal.py 호환)

보강사항:
- 원자적 쓰기 (atomic write)
- 스키마 버전 필드
- 입력 검증
- 경로 안정화
"""
import json, sys, pathlib

def atomic_write(path: pathlib.Path, text: str):
    """원자적 쓰기 유틸리티"""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)

def main(fin, fout):
    """메인 변환 로직"""
    try:
        # 입력 파일 읽기
        data = json.loads(pathlib.Path(fin).read_text(encoding="utf-8"))
        
        # 입력 검증: failures가 배열 아니면 빈 배열로 강제
        failures = data.get("failures", [])
        if not isinstance(failures, list):
            failures = []
            print(f"[WARN] failures field is not array, using empty array", file=sys.stderr)
        
        # 출력 구조 생성 (스키마 버전 포함)
        out = {
            "schema_version": "goal.v1",
            "pass_rate": data.get("pass_rate"),
            "failures": []
        }
        
        # failures 변환 (confidence 기본값 0.5 부여)
        for f in failures:
            f_copy = f.copy() if isinstance(f, dict) else {}
            f_copy["confidence"] = f_copy.get("confidence", 0.5)  # 기본값 설정
            out["failures"].append(f_copy)
        
        # 원자적 쓰기
        output_path = pathlib.Path(fout)
        atomic_write(output_path, json.dumps(out, ensure_ascii=False, indent=2))
        
        print(f"[OK] Converted {len(failures)} failures to goals format")
        
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 failure_to_goal_adapter.py <input.json> <output.json>", file=sys.stderr)
        sys.exit(1)
    
    fin, fout = sys.argv[1], sys.argv[2]
    main(fin, fout)
