import math

def crdt_merge(core_val, rag_candidates):
    """
    core_val: None or value (dict/str/num) from Core
    rag_candidates: list of dicts [{val, sim, recency, prov}]
    """
    if core_val is not None:
        return core_val, {"source":"core"}
    if not rag_candidates:
        return None, {"source":"none"}
    best = max(rag_candidates, key=lambda x: 0.6*x["sim"]+0.2*x["recency"]+0.2*x["prov"])
    return best["val"], {"source":"rag", "score": 0.6*best["sim"]+0.2*best["recency"]+0.2*best["prov"]}

class MonotoneLogit:
    def __init__(self, alpha=0.0, beta_c=2.0, beta_s=1.0, beta_r=0.5, beta_p=0.5, lr=0.05, beta_c_min=1.0):
        self.theta = [alpha,beta_c,beta_s,beta_r,beta_p]
        self.lr = lr
        self.beta_c_min = beta_c_min
    def prob(self, x):
        # x = [core_hit(0/1), sim, recency, prov]
        z = self.theta[0] + self.theta[1]*x[0] + self.theta[2]*x[1] + self.theta[3]*x[2] + self.theta[4]*x[3]
        return 1/(1+math.exp(-z))
    def update(self, x, y):
        p = self.prob(x); g = [(p-y)]  # dL/dalpha
        # grads
        g += [(p-y)*x[0], (p-y)*x[1], (p-y)*x[2], (p-y)*x[3]]
        # SGD
        for i in range(5):
            self.theta[i] -= self.lr * g[i]
        # enforce monotone prior on beta_c
        if self.theta[1] < self.beta_c_min:
            self.theta[1] = self.beta_c_min
