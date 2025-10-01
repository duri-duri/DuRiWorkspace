import argparse
import collections
import datetime
import json
import sys

import yaml
from jsonschema import validate

ap = argparse.ArgumentParser()
ap.add_argument("--family", required=True)
ap.add_argument("--ops", required=True)
ap.add_argument("--schema", required=True)
args = ap.parse_args()

fam = yaml.safe_load(open(args.family))
ops = yaml.safe_load(open(args.ops))
sch = json.load(open(args.schema))

# JSON-Schema 형식검증
validate(fam, sch)

# 불변식: unique ids / members=10 / relations=52 / parent_of DAG / sibling symmetry / parents<=2 / staleness<=review
members = {m["id"]: m for m in fam["members"]}
assert len(members) == len(fam["members"]) == 10
rels = fam["relations"]
assert len(rels) == 52

# parent_of graph
adj = collections.defaultdict(list)
indeg = collections.Counter()
for r in rels:
    if r["type"] == "parent_of":
        adj[r["src"]].append(r["dst"])
        indeg[r["dst"]] += 1
from collections import deque

deg = {u: 0 for u in members}
for u, vs in adj.items():
    for v in vs:
        deg[v] += 1
q = deque([u for u, d in deg.items() if d == 0])
seen = 0
while q:
    u = q.popleft()
    seen += 1
    for v in adj[u]:
        deg[v] -= 1
        if deg[v] == 0:
            q.append(v)
assert seen == len(deg), "cycle detected"

sib = {(r["src"], r["dst"]) for r in rels if r["type"] == "sibling_of"}
for a, b in list(sib):
    assert (b, a) in sib

from collections import Counter

pc = Counter([r["dst"] for r in rels if r["type"] == "parent_of"])
assert all(v <= 2 for v in pc.values())

from datetime import date, timedelta

as_of = date.fromisoformat(fam["as_of"])
assert (date.today() - as_of) <= timedelta(days=fam.get("review_after_days", 180))

print("OK")
