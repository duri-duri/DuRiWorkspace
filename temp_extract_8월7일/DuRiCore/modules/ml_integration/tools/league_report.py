#!/usr/bin/env python3
import json, csv, statistics as st
from pathlib import Path

ART = Path("artifacts_phase1")
LEAGUE = ART / "league.jsonl"
OUT_CSV = ART / "league_summary.csv"
OUT_MD  = ART / "league_report.md"

def load_rows():
    rows = []
    if LEAGUE.exists():
        for line in LEAGUE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows

def main():
    rows = load_rows()
    if not rows:
        print("no league.jsonl yet")
        return

    # CSV 생성 (gate_reason 포함)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "time","idx","valid_r2","test_r2",
            "r2_gap","mse_ratio","nrmse_ratio","gate_pass","gate_reason"
        ])
        for r in rows:
            m = r["metrics"]
            g = m.get("gap_analysis", {})
            w.writerow([
                r.get("time"), r.get("idx"),
                m["validation"]["r2"], m["test"]["r2"],
                g.get("r2_gap"), g.get("mse_ratio"), g.get("nrmse_ratio"),
                r.get("gate_pass"), r.get("gate_reason")
            ])

    # 통계 요약
    tests = [r["metrics"]["test"]["r2"] for r in rows]
    best = max(rows, key=lambda r: r["metrics"]["test"]["r2"])
    pass_rate = sum(1 for r in rows if r.get("gate_pass")) / len(rows)

    base_metrics = json.loads((ART / "final_metrics_valid_test.json").read_text(encoding="utf-8"))
    base_test_r2 = base_metrics["test"]["r2"]

    # Markdown 리포트
    md = []
    md.append("# League Report")
    md.append(f"- 총 시도: **{len(rows)}**")
    md.append(f"- 게이트 통과율: **{pass_rate:.1%}**")
    md.append(f"- Test R² 평균/중앙값: **{st.mean(tests):.4f} / {st.median(tests):.4f}**")
    md.append(f"- 베이스라인 Test R²: **{base_test_r2:.4f}**")
    md.append(f"- 최고 시도: idx {best['idx']} (Test R² **{best['metrics']['test']['r2']:.4f}**)")

    md.append("\n## 최근 10개")
    md.append("| time | idx | valid R² | test R² | r2_gap | mse_ratio | nrmse_ratio | gate | reason |")
    md.append("|---|---:|---:|---:|---:|---:|---:|:--:|:--|")
    for r in rows[-10:]:
        m = r["metrics"]
        g = m.get("gap_analysis", {})
        md.append(
            f"| {r.get('time')} | {r.get('idx')} "
            f"| {m['validation']['r2']:.4f} | {m['test']['r2']:.4f} "
            f"| {g.get('r2_gap', float('nan')):.4f} "
            f"| {g.get('mse_ratio', float('nan')):.3f} "
            f"| {g.get('nrmse_ratio', float('nan')):.3f} "
            f"| {'PASS' if r.get('gate_pass') else 'FAIL'} "
            f"| {r.get('gate_reason', '')} |"
        )

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote: {OUT_CSV}\nwrote: {OUT_MD}")

if __name__ == "__main__":
    main()
