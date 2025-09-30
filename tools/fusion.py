import math

def crdt_merge(core_val, rag_candidates):
    """
    core_val: None or concrete value (dict/str/num) from Core
    rag_candidates: list[{"val":..., "sim":0~1, "recency":0~1, "prov":0~1}]
    """
    if core_val is not None:
        return core_val, {"source":"core"}
    if not rag_candidates:
        return None, {"source":"none"}
    score = lambda x: 0.6*x.get("sim",0)+0.2*x.get("recency",0)+0.2*x.get("prov",0)
    best = max(rag_candidates, key=score)
    return best["val"], {"source":"rag", "score": score(best)}

class MonotoneLogit:
    def __init__(self, alpha=0.0, beta_c=2.0, beta_s=1.2, beta_r=0.6, beta_p=0.8, lr=0.05, beta_c_min=1.0):
        self.theta = [alpha,beta_c,beta_s,beta_r,beta_p]
        self.lr = lr; self.beta_c_min = beta_c_min
    def prob(self, x):
        z = self.theta[0] + sum(t*v for t,v in zip(self.theta[1:], x))
        return 1/(1+math.exp(-z))
    def update(self, x, y):
        p = self.prob(x); grads = [p-y] + [(p-y)*xi for xi in x]
        for i in range(5): self.theta[i] -= self.lr * grads[i]
        if self.theta[1] < self.beta_c_min: self.theta[1] = self.beta_c_min

# 확정기(보류/재탐색 규칙)
def decide_output(thought, cfg, policy_gate_fn, core_snapshot):
    """
    thought: ThinkVerifyDecide.run() 결과
    cfg: runtime_config(dict)
    policy_gate_fn(payload)->bool
    core_snapshot: {"values":{...},"pii_fields":[...]}
    """
    # 0) 증거 임계
    if thought["evidence"] < cfg["tau_evidence"]:
        return {"status":"ABSTAIN","reason":"low_evidence","meta":thought}

    # 1) 정책/무결성
    payload = {
        "mode":"external",
        "output": thought["result"] if isinstance(thought["result"], dict) else {"text": str(thought["result"])},
        "core": core_snapshot
    }
    if not policy_gate_fn(payload):
        return {"status":"ABSTAIN","reason":"policy_block","meta":thought}

    # 2) Core 충돌 모드(HARD에서는 이미 정책에서 막힘; SOFT만 안내)
    if cfg.get("conflict_mode","HARD")=="SOFT" and thought["source"]=="rag":
        pass

    return {"status":"OK","result":thought["result"],"p_good":thought["p_good"],"meta":thought}
