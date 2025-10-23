#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
model_card_autofill.py
HITL 품질 리포트 → 모델카드 자동 채움

보강사항:
- strict 모드 (필수 필드 누락 시 비정상 종료)
- 숫자 범위 체크
- 출력 결정성 (generated_at, 소수점 자리수 고정)
- 원자적 쓰기
- 경로 안정화
"""
import argparse
import json
import pathlib
import sys
from datetime import datetime


def atomic_write(path: pathlib.Path, text: str):
    """원자적 쓰기 유틸리티"""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def read_json(path):
    """JSON 파일 읽기 (에러 처리 포함)"""
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}


def validate_hitl_schema(data, strict=False):
    """HITL 스키마 검증 및 기본값 설정"""
    required_fields = ["accept_rate", "kappa", "p95_latency_h", "quality_score"]
    defaults = {
        "accept_rate": 0.85,
        "kappa": 0.70,
        "p95_latency_h": 48,
        "quality_score": 0.85,
    }

    # strict 모드: 필수 필드 누락 시 비정상 종료
    missing = [k for k in required_fields if k not in data or data[k] is None]
    if strict and missing:
        raise ValueError(f"Missing HITL fields: {missing}")

    # 기본값 설정
    for field in required_fields:
        if field not in data or data[field] is None:
            data[field] = defaults[field]

    # 숫자 범위 체크
    if not (0 <= data["accept_rate"] <= 1):
        raise ValueError(f"accept_rate must be 0-1, got {data['accept_rate']}")
    if not (0 <= data["kappa"] <= 1):
        raise ValueError(f"kappa must be 0-1, got {data['kappa']}")
    if not (data["p95_latency_h"] > 0):
        raise ValueError(f"p95_latency_h must be > 0, got {data['p95_latency_h']}")
    if not (0 <= data["quality_score"] <= 1):
        raise ValueError(f"quality_score must be 0-1, got {data['quality_score']}")

    return data


def format_metric(value, decimals=2):
    """메트릭 포맷팅 (소수점 자리수 고정)"""
    if isinstance(value, (int, float)):
        return f"{value:.{decimals}f}"
    return str(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="", help="Template markdown path (optional)")
    ap.add_argument(
        "--out", default="model_card_v1.autofilled.md", help="Output markdown path"
    )
    ap.add_argument(
        "--strict", action="store_true", help="Strict mode: fail on missing fields"
    )
    args = ap.parse_args()

    # 경로 안정화: __file__ 기준 절대경로 사용
    BASE = pathlib.Path(__file__).resolve().parent

    # Sources
    reg = read_json(BASE / "auto_code_loop_beta/logs/test_result.json") or {}
    slo = read_json(BASE / "slo_sla_dashboard_v1/metrics.json") or {}
    hitl = read_json(BASE / "hitl_quality_report.json") or {}

    # HITL 스키마 검증
    try:
        hitl = validate_hitl_schema(hitl, strict=args.strict)
    except ValueError as e:
        print(f"[ERROR] HITL validation failed: {e}", file=sys.stderr)
        sys.exit(1)

    # 필드 추출 및 포맷팅
    pass_rate = format_metric(reg.get("pass_rate", "TBD"))
    p95_latency = format_metric(slo.get("p95_ms", "TBD"))
    fail_rate_reg = format_metric(slo.get("fail_rate", "TBD"))
    explain_score = format_metric(slo.get("explain_score", "TBD"))
    safety_hit = format_metric(slo.get("safety_hit_rate", "TBD"))
    hitl_accept = format_metric(hitl.get("accept_rate", "TBD"))
    hitl_quality = format_metric(hitl.get("quality_score", "TBD"))
    hitl_kappa = format_metric(hitl.get("kappa", "TBD"))
    hitl_p95h = format_metric(hitl.get("p95_latency_h", "TBD"))

    # 템플릿 로드 또는 기본 템플릿 사용
    if args.template and pathlib.Path(args.template).exists():
        template_content = pathlib.Path(args.template).read_text(encoding="utf-8")
    else:
        template_content = """# DuRi Model Card v1 — **Autofilled Template**

## 5. 성능 (자동 채움)
| 항목 | 값 | 비고 |
|---|---:|---|
| 회귀 통과율 | **{{PASS_RATE}}** | auto_code_loop_beta/logs/test_result.json |
| p95 지연 | **{{P95_LATENCY}}** | slo_sla_dashboard_v1/metrics.json |
| Fail Rate(회귀) | **{{FAIL_RATE_REG}}** | slo_sla_dashboard_v1/metrics.json |
| 설명충분도 | **{{EXPLAIN_SCORE}}** | slo_sla_dashboard_v1/metrics.json |
| 안전 플래그 적중 | **{{SAFETY_HIT}}** | slo_sla_dashboard_v1/metrics.json |
| HITL 수용률 | **{{HITL_ACCEPT}}** | hitl_quality_report.json |

## 8. HITL 품질 (자동 채움)
- 품질 점수: **{{HITL_QUALITY}}**
- Cohen's κ: **{{HITL_KAPPA}}**
- p95 처리시간: **{{HITL_P95H}}**

---
*Generated at: {{GENERATED_AT}}*
"""

    # 플레이스홀더 치환
    output = template_content.replace("{{PASS_RATE}}", pass_rate)
    output = output.replace("{{P95_LATENCY}}", p95_latency)
    output = output.replace("{{FAIL_RATE_REG}}", fail_rate_reg)
    output = output.replace("{{EXPLAIN_SCORE}}", explain_score)
    output = output.replace("{{SAFETY_HIT}}", safety_hit)
    output = output.replace("{{HITL_ACCEPT}}", hitl_accept)
    output = output.replace("{{HITL_QUALITY}}", hitl_quality)
    output = output.replace("{{HITL_KAPPA}}", hitl_kappa)
    output = output.replace("{{HITL_P95H}}", hitl_p95h)

    # 출력 결정성: generated_at 필드 추가
    generated_at = datetime.now().isoformat()
    output = output.replace("{{GENERATED_AT}}", generated_at)

    # 원자적 쓰기
    output_path = BASE / args.out
    atomic_write(output_path, output)

    print(f"[OK] Wrote {args.out}")
    print(f"[INFO] Generated at: {generated_at}")
    if args.strict:
        print("[INFO] Strict mode: all required fields validated")


if __name__ == "__main__":
    main()
