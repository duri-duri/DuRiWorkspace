#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
model_card_autofill.py
- Read metrics from:
  1) auto_code_loop_beta/logs/test_result.json   (Day 15/21 회귀 결과)
  2) slo_sla_dashboard_v1/metrics.json           (운영 지표)
  3) hitl_quality_report.json                    (Day 18 HITL 품질)
- Emit: model_card_v1.autofilled.md
Usage:
  python model_card_autofill.py \
    --template model_card_template.md \
    --out model_card_v1.autofilled.md
Notes:
- If --template not provided, use built-in template.
- Missing files tolerated; fields become "TBD".
"""
import argparse
import datetime
import json
import pathlib


def read_json(path):
    p = pathlib.Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def pct(x, digits=2):
    try:
        return f"{round(float(x)*100.0, digits)}%"
    except Exception:
        return "TBD"


def ms(x):
    try:
        return f"{int(round(float(x)))} ms"
    except Exception:
        return "TBD"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="", help="Template markdown path (optional)")
    ap.add_argument(
        "--out", default="model_card_v1.autofilled.md", help="Output markdown path"
    )
    args = ap.parse_args()

    # Sources
    reg = read_json("auto_code_loop_beta/logs/test_result.json") or {}
    slo = read_json("slo_sla_dashboard_v1/metrics.json") or {}
    hitl = read_json("hitl_quality_report.json") or {}

    # Derive fields
    pass_rate = reg.get("pass_rate")  # 0.0~1.0 or e.g., 0.83
    failures = reg.get("failures", [])
    fail_rate_reg = slo.get("fail_rate_reg")  # optional
    p95_latency_ms = slo.get("p95_ms") or slo.get("p95_latency_ms")
    safety_hit = slo.get("safety_flag_precision") or slo.get("safety_hit_rate")
    explain_score = slo.get("explain_sufficiency") or slo.get("explain_score")
    hitl_accept = hitl.get("accept_rate") or hitl.get("hitl_accept_rate")
    kappa = hitl.get("kappa")
    p95_h = hitl.get("p95_latency_h")
    quality = hitl.get("quality_score")

    # Fall-backs from sample/dummy values
    if pass_rate is None and reg:
        # try reconstruct from counts if present
        passed = reg.get("passed")
        total = reg.get("total")
        if passed is not None and total:
            pass_rate = passed / total
    # Format
    pass_rate_pct = (
        pct(pass_rate) if pass_rate is not None and pass_rate <= 1 else f"{pass_rate}%"
    )
    p95_latency_fmt = ms(p95_latency_ms) if p95_latency_ms is not None else "TBD"
    fail_rate_reg_pct = (
        pct(fail_rate_reg)
        if isinstance(fail_rate_reg, (int, float)) and fail_rate_reg <= 1
        else (f"{fail_rate_reg}%" if fail_rate_reg is not None else "TBD")
    )
    safety_hit_pct = (
        pct(safety_hit)
        if isinstance(safety_hit, (int, float)) and safety_hit <= 1
        else (f"{safety_hit}%" if safety_hit is not None else "TBD")
    )
    explain_score_fmt = (
        f"{explain_score:.2f} / 5.0"
        if isinstance(explain_score, (int, float))
        else "TBD"
    )
    hitl_accept_pct = (
        pct(hitl_accept)
        if isinstance(hitl_accept, (int, float)) and hitl_accept <= 1
        else (f"{hitl_accept}%" if hitl_accept is not None else "TBD")
    )
    kappa_fmt = f"{kappa:.2f}" if isinstance(kappa, (int, float)) else "TBD"
    p95_h_fmt = f"{p95_h} h" if isinstance(p95_h, (int, float)) else "TBD"
    quality_fmt = (
        f"{quality:.0f}%"
        if isinstance(quality, (int, float)) and quality <= 1
        else (
            f"{quality:.0f}%"
            if isinstance(quality, (int, float)) and quality > 1
            else "TBD"
        )
    )

    # Build markdown (use template if provided)
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    template_path = pathlib.Path(args.template)
    if template_path.exists():
        tpl = template_path.read_text(encoding="utf-8")
    else:
        tpl = f"""# DuRi Model Card v1 — **Autofilled ({now})**
_Revision_: {now}
_Channel_: Canary (10%) / Internal

## 5. 성능 (자동 채움)
| 항목 | 값 | 비고 |
|---|---:|---|
| 회귀 통과율 | **{pass_rate_pct}** | auto_code_loop_beta/logs/test_result.json |
| p95 지연 | **{p95_latency_fmt}** | slo_sla_dashboard_v1/metrics.json |
| Fail Rate(회귀) | **{fail_rate_reg_pct}** | slo_sla_dashboard_v1/metrics.json |
| 설명충분도 | **{explain_score_fmt}** | slo_sla_dashboard_v1/metrics.json |
| 안전 플래그 적중 | **{safety_hit_pct}** | slo_sla_dashboard_v1/metrics.json |
| HITL 수용률 | **{hitl_accept_pct}** | hitl_quality_report.json |

## 8. HITL 품질 (자동 채움)
- 품질 점수: **{quality_fmt}**
- Cohen’s κ: **{kappa_fmt}**
- p95 처리시간: **{p95_h_fmt}**
"""

    # If template has placeholders, replace them
    # Supported placeholders: {{PASS_RATE}}, {{P95_LATENCY}}, {{FAIL_RATE_REG}}, {{EXPLAIN_SCORE}}, {{SAFETY_HIT}}, {{HITL_ACCEPT}}, {{HITL_QUALITY}}, {{HITL_KAPPA}}, {{HITL_P95H}}
    repl = {
        "{{PASS_RATE}}": pass_rate_pct,
        "{{P95_LATENCY}}": p95_latency_fmt,
        "{{FAIL_RATE_REG}}": fail_rate_reg_pct,
        "{{EXPLAIN_SCORE}}": explain_score_fmt,
        "{{SAFETY_HIT}}": safety_hit_pct,
        "{{HITL_ACCEPT}}": hitl_accept_pct,
        "{{HITL_QUALITY}}": quality_fmt,
        "{{HITL_KAPPA}}": kappa_fmt,
        "{{HITL_P95H}}": p95_h_fmt,
    }
    out = tpl
    for k, v in repl.items():
        out = out.replace(k, v)

    pathlib.Path(args.out).write_text(out, encoding="utf-8")
    print(f"[OK] Wrote {args.out}")


if __name__ == "__main__":
    main()
