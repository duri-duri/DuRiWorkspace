# tools/e2e_capsule_test.py
import json
from datetime import datetime, timezone

from tools.capsule import make_capsule

# 1) 내부 모듈
from tools.db import append_audit, insert_answer_capsule, upsert_canonical_bt, with_tx
from tools.fusion import MonotoneLogit, crdt_merge

# 2) 정책 게이트 (있으면 import, 없으면 폴백)
try:
    from tools.policy_gate import opa_allow as policy_allow
except Exception:

    def policy_allow(payload: dict) -> bool:
        # Rego와 등가의 간단 폴백
        mode = payload.get("mode")
        core = payload.get("core", {})
        out = payload.get("output", {})
        pii_fields = set(core.get("pii_fields", []))
        if mode == "external" and any(f in out and out[f] is not None for f in pii_fields):
            return False
        core_vals = core.get("values", {})
        for k, v in core_vals.items():
            if k in out and out[k] != v and v is not None and out[k] is not None:
                return False
        return True


def _utcnow():
    return datetime.now(timezone.utc)


def main():
    print("=== PZTA-CRA E2E: start ===")

    # ---- A) Core upsert (예: 공개 이름) ----
    bundle_hash = "deadbeef" * 8  # 샘플; 실제는 CI 번들 해시 사용 권장
    version = "v1.0"
    core_key = "profile.name_pub"
    core_val = "두리"

    def _upsert(cur):
        upsert_canonical_bt(
            cur,
            key=core_key,
            value={"name_pub": core_val},
            bundle_hash=bundle_hash,
            version=version,
            valid_from=_utcnow(),
            valid_to="9999-12-31",
        )

    with_tx(_upsert)
    print("• Core upsert OK")

    # ---- B) 후보 생성 + Fusion ----
    rag_candidates = [{"val": {"name_pub": "두리"}, "sim": 0.86, "recency": 0.7, "prov": 0.9}]
    fused_val, meta = crdt_merge(core_val={"name_pub": core_val}, rag_candidates=rag_candidates)
    # crdt_merge에서 core가 있으면 core 선택 → fused_val은 dict가 아닌 문자열일 수 있으므로 정규화
    if isinstance(fused_val, str):
        fused_val = {"name_pub": fused_val}
    print(f"• Fusion source={meta.get('source')} => {fused_val}")

    # ---- C) 정책 게이트 ----
    payload = {
        "mode": "external",
        "core": {
            "values": {"name_pub": core_val},
            "pii_fields": ["name_priv", "email_priv"],
        },
        "output": fused_val,
    }
    allowed = policy_allow(payload)
    print(f"• Policy allow? {allowed}")

    # ---- D) 캡슐 생성/저장 or 충돌 감사 ----
    if allowed:
        # 모노톤 로짓 예시 확률
        p = MonotoneLogit().prob([1, 0.9, 0.8, 0.9])
        cap = make_capsule(
            query="두리의 공개 이름은?",
            core_tag=version,
            bundle_hash=bundle_hash,
            rag_docs=[{"hash": "doc1", "sim": 0.86, "age_days": 3}],
            fusion_w={"prob": p},
            model="gpt-x",
            prompt_hash="phash",
            seed=42,
            tee_attestation=None,
            output_text=json.dumps(fused_val, ensure_ascii=False),
            tokens=128,
            latency_ms=123,
        )

        def _write(cur):
            insert_answer_capsule(cur, cap)
            append_audit(cur, "capsule_recorded", {"qid": cap["qid"], "prob": p, "meta": meta})

        with_tx(_write)
        print(f"• Capsule stored: qid={cap['qid']}")
    else:

        def _audit(cur):
            append_audit(cur, "core_conflict_blocked", {"payload": payload})

        with_tx(_audit)
        print("• Blocked by policy; audit appended")

    # ---- E) 간단 조회(정상 기록 확인) ----
    def _read(cur):
        cur.execute("select count(*) as n from answer_ledger")
        n_caps = cur.fetchone()["n"]
        cur.execute("select count(*) as n from audit_ledger")
        n_audit = cur.fetchone()["n"]
        return n_caps, n_audit

    caps, audits = with_tx(_read)
    print(f"• Rows => answer_ledger: {caps}, audit_ledger: {audits}")

    print("=== PZTA-CRA E2E: done ===")


if __name__ == "__main__":
    main()
