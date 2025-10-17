#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
입력: TSV with columns:
- query_id
- domain            # 예: law/finance/health
- rank              # 1..k
- is_correct        # 1 or 0
- ideal_relevant    # 쿼리당 이상적 관련 문서 수(옵션: 없으면 is_correct 합으로 대체)
사용:
  python3 scripts/metrics/compute_metrics.py --in .reports/train/day64/LATEST.tsv --k 3 --out .reports/metrics/day66_metrics.tsv
"""
import argparse
import collections
import csv
import math
import statistics
import sys


def ndcg_at_k(labels, k):
    gains = [
        (1.0 / math.log2(i + 2)) if labels[i] == 1 else 0.0 for i in range(min(k, len(labels)))
    ]
    dcg = sum(gains)
    ideal = sorted(labels, reverse=True)
    igains = [(1.0 / math.log2(i + 2)) if ideal[i] == 1 else 0.0 for i in range(min(k, len(ideal)))]
    idcg = sum(igains) or 1.0
    return dcg / idcg


def mrr(labels):
    for i, lab in enumerate(labels, start=1):
        if lab == 1:
            return 1.0 / i
    return 0.0


def oracle_recall(labels, k):
    tot = sum(labels)
    if tot == 0:
        return 0.0
    return sum(labels[:k]) / float(tot)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--out", dest="outp", required=True)
    args = ap.parse_args()

    by_q = collections.defaultdict(list)
    by_q_dom = {}
    with open(args.inp, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        need = {"query_id", "rank", "is_correct"}
        miss = need - set([c.strip() for c in r.fieldnames or []])
        if miss:
            print(f"[err] missing columns: {sorted(miss)}", file=sys.stderr)
            sys.exit(2)
        for row in r:
            q = row["query_id"].strip()
            dom = row.get("domain", "").strip() or "unknown"
            lbl = 1 if str(row["is_correct"]).strip() in ("1", "true", "True") else 0
            rk = int(row["rank"])
            by_q[q].append((rk, lbl))
            by_q_dom[q] = dom
    # sort by rank asc per query
    for q in by_q:
        by_q[q].sort(key=lambda x: x[0])

    # compute per query
    rows = []
    for q, items in by_q.items():
        labels = [lbl for _, lbl in items]
        k = args.k
        rows.append(
            {
                "query_id": q,
                "domain": by_q_dom.get(q, "unknown"),
                f"ndcg@{k}": round(ndcg_at_k(labels, k), 6),
                "mrr": round(mrr(labels), 6),
                f"oracle_recall@{k}": round(oracle_recall(labels, k), 6),
            }
        )

    # aggregate by domain & overall
    def agg(metric):
        vals = [float(r[metric]) for r in rows]
        return round(statistics.mean(vals), 6) if vals else 0.0

    domains = collections.defaultdict(list)
    for r in rows:
        domains[r["domain"]].append(r)

    with open(args.outp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        k = args.k
        header = ["scope", "domain", "count", f"ndcg@{k}", "mrr", f"oracle_recall@{k}"]
        w.writerow(header)

        # per domain
        for d, rs in sorted(domains.items()):
            w.writerow(
                [
                    "domain",
                    d,
                    len(rs),
                    round(statistics.mean([x[f"ndcg@{k}"] for x in rs]), 6),
                    round(statistics.mean([x["mrr"] for x in rs]), 6),
                    round(statistics.mean([x[f"oracle_recall@{k}"] for x in rs]), 6),
                ]
            )

        # overall
        w.writerow(
            [
                "all",
                "-",
                len(rows),
                agg(f"ndcg@{k}"),
                agg("mrr"),
                agg(f"oracle_recall@{k}"),
            ]
        )


if __name__ == "__main__":
    main()


