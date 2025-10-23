import hashlib
import time
import uuid


def sha256s(s):
    return hashlib.sha256(s.encode()).hexdigest()


def make_capsule(
    query,
    core_tag,
    bundle_hash,
    rag_docs,
    fusion_w,
    model,
    prompt_hash,
    seed,
    tee_attestation=None,
    output_text="",
    tokens=0,
    latency_ms=0,
):
    return {
        "qid": f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}-{uuid.uuid4()}",
        "core": {"tag": core_tag, "bundle": bundle_hash},
        "rag": [
            {
                "doc": d["hash"],
                "ver": d.get("ver", ""),
                "sim": d.get("sim", 0.0),
                "age_days": d.get("age_days", 0),
            }
            for d in rag_docs
        ],
        "fusion": {"w": fusion_w, "rule": "crdt+monotone-logit"},
        "runtime": {
            "model": model,
            "prompt": prompt_hash,
            "seed": seed,
            "tee_attestation": tee_attestation,
        },
        "output": {
            "hash": sha256s(output_text),
            "tokens": tokens,
            "latency_ms": latency_ms,
        },
        "query_hash": sha256s(query),
    }
