import json, collections, argparse

SEVERITY = {"Validation": 3, "Transient": 1, "System": 4, "Spec": 2}

MAP = {
  "Validation": {"goal_type": "Improve_Facts", "ops": ["augment_retrieval", "add_faq_pairs"]},
  "Transient":  {"goal_type": "Stabilize_IO",  "ops": ["retry_policy", "debounce"]},
  "System":     {"goal_type": "Hardening",     "ops": ["sandbox_limit", "timeout_tune"]},
  "Spec":       {"goal_type": "Clarify_Policy","ops": ["spec_update", "prompt_guard"]}
}

def main(inp, outp):
    data = json.load(open(inp, encoding="utf-8"))
    cnt = collections.Counter([f.get("type") for f in data.get("failures", [])])
    goals = []
    for f in data.get("failures", []):
        m = MAP.get(f.get("type"), {"goal_type":"Triage","ops":["manual_review"]})
        priority = SEVERITY.get(f.get("type"),2) + min(3, cnt[f.get("type")])
        goals.append({"goal_type":m["goal_type"],"spec":f,"priority":priority,"suggested_data_ops":m["ops"]})
    json.dump(sorted(goals, key=lambda x: -x["priority"]), open(outp,"w", encoding="utf-8"), indent=2, ensure_ascii=False)

if __name__=="__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", required=True)
    args = ap.parse_args()
    main(args.inp, args.outp)
