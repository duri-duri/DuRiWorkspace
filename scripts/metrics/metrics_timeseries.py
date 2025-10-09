#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scan .reports/metrics/day*_metrics.tsv
 -> call scripts/metrics/export_prom.sh for each
 -> parse Prom text
 -> extract ALL-scope metrics (k=3)
 -> write CSV and weekly Markdown summary.

Stdlib only.
"""

import argparse
import csv
import datetime as dt
import glob
import os
import re
import statistics as stats
import subprocess
from typing import Dict, List, Optional, Tuple

PROM_EXPORT = "scripts/metrics/export_prom.sh"

RE_SAMPLE_LABELED = re.compile(r"^([A-Za-z_:][A-Za-z0-9_:]*)\{([^}]*)\}\s+([^\s]+)$")
RE_SAMPLE_PLAIN = re.compile(r"^([A-Za-z_:][A-Za-z0-9_:]*)\s+([^\s]+)$")
RE_LABEL = re.compile(r'\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"(.*)"\s*')


def parse_num(s: str) -> float:
    if s in ("+Inf", "Inf"):
        return float("inf")
    if s == "-Inf":
        return float("-inf")
    if s == "NaN":
        return float("nan")
    return float(s)


def parse_labels(s: str) -> Dict[str, str]:
    # naive but fine for Prom text (no escaped quotes expected in our labels)
    out = {}
    for piece in s.split(","):
        m = RE_LABEL.match(piece)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def parse_prom_text(text: str) -> List[Tuple[str, Dict[str, str], float]]:
    """Return list of (name, labels, value)."""
    out = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        m = RE_SAMPLE_LABELED.match(line)
        if m:
            name = m.group(1)
            labels = parse_labels(m.group(2))
            val = parse_num(m.group(3))
            out.append((name, labels, val))
            continue
        m = RE_SAMPLE_PLAIN.match(line)
        if m:
            name = m.group(1)
            labels = {}
            val = parse_num(m.group(2))
            out.append((name, labels, val))
    return out


def pick_value(
    samples: List[Tuple[str, Dict[str, str], float]], name: str, must: Dict[str, str]
) -> Optional[float]:
    for n, lbl, v in samples:
        if n != name:
            continue
        ok = True
        for k, exp in must.items():
            if lbl.get(k) != exp:
                ok = False
                break
        if ok:
            return v
    return None


def export_prom(tsv_path: str) -> str:
    cp = subprocess.run(["bash", PROM_EXPORT, tsv_path], check=True, text=True, capture_output=True)
    return cp.stdout


def rolling(values: List[Optional[float]], window: int) -> List[Optional[float]]:
    out = []
    buf: List[float] = []
    for i, v in enumerate(values):
        if v is not None:
            buf.append(v)
        # keep last `window` non-None values
        trimmed = [x for x in buf[-window:] if x is not None]
        out.append(stats.mean(trimmed) if trimmed else None)
    return out


def rolling_std(values: List[Optional[float]], window: int) -> List[Optional[float]]:
    out = []
    buf: List[float] = []
    for i, v in enumerate(values):
        if v is not None:
            buf.append(v)
        trimmed = [x for x in buf[-window:] if x is not None]
        if len(trimmed) >= 2:
            out.append(stats.pstdev(trimmed))
        else:
            out.append(None)
    return out


def fmt(x: Optional[float], digits=6) -> str:
    if x is None:
        return ""
    return f"{x:.{digits}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=".reports/metrics")
    ap.add_argument("--outdir", default=".reports/timeseries")
    ap.add_argument("--period", type=int, default=7)
    ap.add_argument("--k", default="3")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    files = sorted(glob.glob(os.path.join(args.input, "day*_metrics.tsv")))
    if not files:
        print(f"no files matched under {args.input}")
        return

    rows = []
    for tsv in files:
        prom = export_prom(tsv)
        samples = parse_prom_text(prom)

        ts = pick_value(samples, "duri_metrics_generated_seconds", {})
        if ts is None:
            # fallback to file mtime if missing
            epoch = int(os.path.getmtime(tsv))
        else:
            epoch = int(ts)

        when = dt.datetime.utcfromtimestamp(epoch)
        date = when.date().isoformat()

        ndcg = pick_value(samples, "duri_ndcg_at_k", {"k": args.k, "scope": "all", "domain": "ALL"})
        mrr = pick_value(samples, "duri_mrr", {"scope": "all", "domain": "ALL"})
        recall = pick_value(
            samples, "duri_oracle_recall_at_k", {"k": args.k, "scope": "all", "domain": "ALL"}
        )
        guard = pick_value(samples, "duri_guard_last_exit_code", {})  # optional
        up = pick_value(samples, "duri_exporter_up", {})  # optional

        rows.append(
            {
                "date": date,
                "epoch": epoch,
                "file": os.path.basename(tsv),
                "ndcg_k": ndcg,
                "mrr": mrr,
                "recall_k": recall,
                "guard_exit": guard,
                "exporter_up": up,
            }
        )

    # sort by epoch just in case
    rows.sort(key=lambda r: r["epoch"])

    # compute rolling windows
    ndcg_series = [r["ndcg_k"] for r in rows]
    mrr_series = [r["mrr"] for r in rows]

    ma_ndcg = rolling(ndcg_series, args.period)
    sd_ndcg = rolling_std(ndcg_series, args.period)
    ma_mrr = rolling(mrr_series, args.period)
    sd_mrr = rolling_std(mrr_series, args.period)

    for r, ma_n, sd_n, ma_m, sd_m in zip(rows, ma_ndcg, sd_ndcg, ma_mrr, sd_mrr):
        r["ndcg_ma"] = ma_n
        r["ndcg_std"] = sd_n
        r["mrr_ma"] = ma_m
        r["mrr_std"] = sd_m

    # DoD / WoW deltas for NDCG
    def delta(a: Optional[float], b: Optional[float]) -> Optional[float]:
        if a is None or b is None:
            return None
        return a - b

    if len(rows) >= 2:
        rows[-1]["ndcg_dod"] = delta(rows[-1]["ndcg_k"], rows[-2]["ndcg_k"])
        rows[-1]["mrr_dod"] = delta(rows[-1]["mrr"], rows[-2]["mrr"])
    if len(rows) > args.period:
        rows[-1]["ndcg_wow"] = delta(rows[-1]["ndcg_k"], rows[-1 - args.period]["ndcg_k"])
        rows[-1]["mrr_wow"] = delta(rows[-1]["mrr"], rows[-1 - args.period]["mrr"])

    # write CSV
    csv_path = os.path.join(args.outdir, "metrics_all_scope.csv")
    fieldnames = [
        "date",
        "epoch",
        "file",
        "ndcg_k",
        "ndcg_ma",
        "ndcg_std",
        "ndcg_dod",
        "ndcg_wow",
        "mrr",
        "mrr_ma",
        "mrr_std",
        "mrr_dod",
        "mrr_wow",
        "recall_k",
        "guard_exit",
        "exporter_up",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "date": r["date"],
                    "epoch": r["epoch"],
                    "file": r["file"],
                    "ndcg_k": r["ndcg_k"],
                    "ndcg_ma": r.get("ndcg_ma"),
                    "ndcg_std": r.get("ndcg_std"),
                    "ndcg_dod": r.get("ndcg_dod"),
                    "ndcg_wow": r.get("ndcg_wow"),
                    "mrr": r["mrr"],
                    "mrr_ma": r.get("mrr_ma"),
                    "mrr_std": r.get("mrr_std"),
                    "mrr_dod": r.get("mrr_dod"),
                    "mrr_wow": r.get("mrr_wow"),
                    "recall_k": r["recall_k"],
                    "guard_exit": r.get("guard_exit"),
                    "exporter_up": r.get("exporter_up"),
                }
            )

    # write weekly markdown
    latest = rows[-1]
    md_name = f"weekly_{os.path.splitext(latest['file'])[0]}.md"
    md_path = os.path.join(args.outdir, md_name)
    recent = rows[-args.period :] if len(rows) >= args.period else rows

    def rfmt(v):
        return "-" if v is None else (f"{v:.4f}" if isinstance(v, float) else str(v))

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Weekly Report (k={args.k}, scope=ALL)\n\n")
        f.write(f"- Period: last {len(recent)} days (target={args.period})\n")
        f.write(f"- Latest date: **{latest['date']}**\n")
        f.write(
            f"- nDCG: {rfmt(latest['ndcg_k'])} | MA{args.period}: {rfmt(latest.get('ndcg_ma'))} | STD{args.period}: {rfmt(latest.get('ndcg_std'))}\n"
        )
        f.write(
            f"- MRR: {rfmt(latest['mrr'])} | MA{args.period}: {rfmt(latest.get('mrr_ma'))} | STD{args.period}: {rfmt(latest.get('mrr_std'))}\n"
        )
        f.write(
            f"- DoD Δ (nDCG/MRR): {rfmt(latest.get('ndcg_dod'))} / {rfmt(latest.get('mrr_dod'))}\n"
        )
        f.write(
            f"- WoW Δ (nDCG/MRR): {rfmt(latest.get('ndcg_wow'))} / {rfmt(latest.get('mrr_wow'))}\n"
        )
        f.write("\n## Last days\n\n")
        f.write("| date | nDCG | MRR | recall | nDCG_MA | nDCG_STD |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for r in recent:
            f.write(
                f"| {r['date']} | {rfmt(r['ndcg_k'])} | {rfmt(r['mrr'])} | {rfmt(r['recall_k'])} | {rfmt(r.get('ndcg_ma'))} | {rfmt(r.get('ndcg_std'))} |\n"
            )

    print(f"✓ CSV: {csv_path}")
    print(f"✓ MD : {md_path}")


if __name__ == "__main__":
    main()
