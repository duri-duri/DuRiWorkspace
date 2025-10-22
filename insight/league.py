from __future__ import annotations

import dataclasses
import json
import math
import statistics
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml  # pyyaml 필요

from .metrics import evaluate_text  # Phase 19-1에서 이미 존재


@dataclasses.dataclass
class Sample:
    id: str
    group: str
    prompt: Optional[str]
    references: List[str]
    # 내장 candidates는 옵션
    candidates: List[Dict[str, str]]  # [{tag,text}, ...]


@dataclasses.dataclass
class GroupCfg:
    id: str
    weight: float = 1.0


@dataclasses.dataclass
class SampleSet:
    version: int
    name: str
    groups: Dict[str, GroupCfg]
    samples: List[Sample]


def load_sampleset(path: Path) -> SampleSet:
    d = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    groups = {
        g["id"]: GroupCfg(id=g["id"], weight=float(g.get("weight", 1.0)))
        for g in d.get("groups", [])
    }
    samples: List[Sample] = []
    for s in d.get("samples", []):
        samples.append(
            Sample(
                id=str(s["id"]),
                group=str(s["group"]),
                prompt=s.get("prompt"),
                references=[str(r) for r in (s.get("references") or [])],
                candidates=[
                    {"tag": c.get("tag", "default"), "text": c.get("text", "")}
                    for c in (s.get("candidates") or [])
                ],
            )
        )
    return SampleSet(
        version=int(d.get("version", 1)),
        name=str(d.get("name", "unnamed")),
        groups=groups,
        samples=samples,
    )


def load_outputs_jsonl(path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
    """id -> {'text':..., 'tag':...}"""
    if not path:
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            j = json.loads(line)
            sid = str(j["id"])
            out[sid] = {"text": j["text"], "tag": j.get("tag", "current")}
    return out


def _pick_candidate(sample: Sample, outputs: Dict[str, Dict[str, Any]]) -> Tuple[str, str]:
    """returns (tag, text). priority: external outputs > built-in candidate(baseline) > first candidate > ''"""
    if sample.id in outputs:
        o = outputs[sample.id]
        return str(o.get("tag", "current")), str(o.get("text", ""))
    if sample.candidates:
        # prefer 'baseline' if exists
        base = next((c for c in sample.candidates if c.get("tag") == "baseline"), None)
        c = base or sample.candidates[0]
        return str(c.get("tag", "candidate")), str(c.get("text", ""))
    return "none", ""


def evaluate_league(
    sampleset: SampleSet, outputs_path: Optional[Path], run_name: str = "current"
) -> Dict[str, Any]:
    outs = load_outputs_jsonl(outputs_path)
    per_sample = []
    group_scores: Dict[str, List[float]] = {}

    for s in sampleset.samples:
        tag, text = _pick_candidate(s, outs)
        res = evaluate_text(text, references=s.references, detailed=True)
        score = float(res["composite_score"])
        per_sample.append(
            {
                "id": s.id,
                "group": s.group,
                "tag": tag,
                "prompt": s.prompt,
                "text": text,
                "composite_score": score,
                "details": {k: v for k, v in res.items() if k != "composite_score"},
            }
        )
        group_scores.setdefault(s.group, []).append(score)

    groups = []
    overall_scores = []
    for gid, arr in group_scores.items():
        avg = float(sum(arr) / len(arr)) if arr else 0.0
        overall_scores.extend(arr)
        groups.append(
            {
                "group": gid,
                "count": len(arr),
                "avg_composite": avg,
            }
        )

    report = {
        "version": 1,
        "sampleset": {
            "name": sampleset.name,
            "total": len(sampleset.samples),
        },
        "run": {
            "name": run_name,
        },
        "overall": {
            "avg_composite": (
                float(sum(overall_scores) / len(overall_scores)) if overall_scores else 0.0
            ),
            "min": float(min(overall_scores)) if overall_scores else 0.0,
            "max": float(max(overall_scores)) if overall_scores else 0.0,
            "std": (float(statistics.pstdev(overall_scores)) if len(overall_scores) > 1 else 0.0),
        },
        "by_group": groups,
        "results": per_sample,
    }
    return report


def save_md_table(report: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"# 📊 League Report — {report['sampleset']['name']} ({report['run']['name']})")
    o = report["overall"]
    lines += [
        "",
        f"- **Avg**: `{o['avg_composite']:.3f}`  •  **Min**: `{o['min']:.3f}`  •  **Max**: `{o['max']:.3f}`  •  **Std**: `{o['std']:.3f}`",
        "",
        "## Group Averages",
        "",
        "| Group | N | Avg |",
        "|---|---:|---:|",
    ]
    for g in report["by_group"]:
        lines.append(f"| `{g['group']}` | {g['count']} | `{g['avg_composite']:.3f}` |")

    # Top/Bottom
    results = sorted(report["results"], key=lambda x: x["composite_score"], reverse=True)
    head = results[:5]
    tail = results[-5:] if len(results) > 5 else []

    def row(r):
        txt = r["text"]
        if len(txt) > 60:
            txt = txt[:60] + "..."
        return f"| `{r['id']}` | `{r['group']}` | `{r['composite_score']:.3f}` | `{txt}` |"

    lines += ["", "## Top 5", "", "| ID | Group | Score | Text |", "|---|---|---:|---|"]
    for r in head:
        lines.append(row(r))

    if tail:
        lines += [
            "",
            "## Bottom 5",
            "",
            "| ID | Group | Score | Text |",
            "|---|---|---:|---|",
        ]
        for r in reversed(tail):  # ascending
            lines.append(row(r))

    return "\n".join(lines)


def regress(
    baseline: Dict[str, Any],
    current: Dict[str, Any],
    threshold_overall: float = 0.005,
    threshold_group: float = 0.010,
) -> Dict[str, Any]:
    """Return dict with deltas and pass/fail decision."""

    def to_map_by_group(rep: Dict[str, Any]) -> Dict[str, float]:
        return {g["group"]: float(g["avg_composite"]) for g in rep.get("by_group", [])}

    cur_o = float(current["overall"]["avg_composite"])
    base_o = float(baseline["overall"]["avg_composite"])
    delta_o = cur_o - base_o

    base_g = to_map_by_group(baseline)
    cur_g = to_map_by_group(current)
    group_rows = []
    worst_drop = 0.0
    for gid in sorted(set(base_g) | set(cur_g)):
        b = base_g.get(gid, 0.0)
        c = cur_g.get(gid, 0.0)
        d = c - b
        worst_drop = min(worst_drop, d)
        group_rows.append({"group": gid, "baseline": b, "current": c, "delta": d})

    ok_overall = delta_o >= -abs(threshold_overall)
    ok_groups = all(row["delta"] >= -abs(threshold_group) for row in group_rows)
    passed = bool(ok_overall and ok_groups)

    return {
        "passed": passed,
        "overall": {
            "baseline": base_o,
            "current": cur_o,
            "delta": delta_o,
            "threshold": -abs(threshold_overall),
        },
        "by_group": group_rows,
        "threshold_group": -abs(threshold_group),
        "worst_group_drop": worst_drop,
    }


def regression_md(summary: Dict[str, Any]) -> str:
    s = summary
    lines = []
    status = "✅ PASS" if s["passed"] else "❌ FAIL"
    lines += [f"# 🧪 Regression Summary — {status}", ""]
    o = s["overall"]
    lines += [
        "## Overall",
        "",
        f"- Baseline: `{o['baseline']:.3f}`  •  Current: `{o['current']:.3f}`  •  Δ: `{o['delta']:.3f}`  •  Threshold: `{o['threshold']:.3f}`",
        "",
        "## By Group",
        "",
        "| Group | Baseline | Current | Δ |",
        "|---|---:|---:|---:|",
    ]
    for r in s["by_group"]:
        lines.append(
            f"| `{r['group']}` | `{r['baseline']:.3f}` | `{r['current']:.3f}` | `{r['delta']:.3f}` |"
        )
    lines += [
        "",
        f"**Worst group drop:** `{s['worst_group_drop']:.3f}`  •  **Group threshold:** `{s['threshold_group']:.3f}`",
    ]
    return "\n".join(lines)
