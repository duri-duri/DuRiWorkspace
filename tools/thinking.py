import random, time, statistics
from .fusion import crdt_merge, MonotoneLogit

def evidence_score(rag_docs):
    """근거 점수: 유사도/최근성/출처 품질을 0~1로 집계(가중 평균)."""
    if not rag_docs: return 0.0
    # sim(0.6) + recency(0.2) + provenance(0.2)
    vals = [0.6*d.get("sim",0)+0.2*d.get("recency",0)+0.2*d.get("prov",0) for d in rag_docs]
    return sum(vals)/len(vals)

def self_consistency_samples(generator_fn, k=5, depth=2, seed=None):
    """모델/프롬프트로 k개 사고샘플 생성(자기일치) -> 후보/메타 반환."""
    if seed is not None: random.seed(seed)
    cands = []
    for _ in range(k):
        ans, meta = generator_fn(depth=depth)  # meta: {"rag_docs":[...], "sim":float,...}
        cands.append((ans, meta))
    # 다수결 + 평균 근거 점수
    tally = {}
    for a,_ in cands:
        tally[a] = tally.get(a,0)+1
    majority = max(tally.items(), key=lambda x:x[1])[0]
    avg_e = statistics.mean([evidence_score(m.get("rag_docs",[])) for _,m in cands])
    return majority, avg_e, cands

class ThinkVerifyDecide:
    def __init__(self, cfg, logit:MonotoneLogit):
        self.cfg = cfg; self.logit = logit

    def run(self, core_values:dict, generator_fn, rag_candidates:list, mode="external"):
        # 1) self-consistency
        ans_sc, e_score, samples = self_consistency_samples(
            generator_fn, k=self.cfg["self_consistency"]["k"],
            depth=self.cfg["self_consistency"]["depth"]
        )
        # 2) 결정형 병합(CRDT 하한)
        core_hit = core_values.get("value", None) is not None
        merged, mmeta = crdt_merge(core_values.get("value"), rag_candidates)
        # 3) 적응형 로짓 스코어(확률)
        sim = max([d.get("sim",0.0) for d in rag_candidates], default=0.0)
        rec = max([d.get("recency",0.0) for d in rag_candidates], default=0.0)
        prov = max([d.get("prov",0.0) for d in rag_candidates], default=0.0)
        p_good = self.logit.prob([1 if core_hit else 0, sim, rec, prov])

        result = merged if core_hit else ans_sc
        return {
            "result": result,
            "evidence": e_score,
            "p_good": p_good,
            "samples": samples,
            "source": mmeta.get("source","core" if core_hit else "rag"),
            "rag_candidates": rag_candidates
        }


