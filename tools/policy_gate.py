import json, subprocess, shutil

def opa_allow(payload: dict, rego_path="tools/opa_policies/guard.rego"):
    """OPA가 있으면 사용, 없으면 폴백 규칙으로 검증."""
    if shutil.which("opa"):
        p = subprocess.run(
            ["opa","eval","-f","pretty","-I","-d",rego_path,"data.duri.guard.allow"],
            input=json.dumps({"input":payload}).encode(), capture_output=True
        )
        return (p.returncode==0) and ("true" in p.stdout.decode().lower())
    # 폴백: 외부모드에서 PII 차단 + Core≻RAG
    mode = payload.get("mode","external")
    output = payload.get("output",{})
    core = payload.get("core",{})
    pii_fields = core.get("pii_fields",["name_priv"])
    if mode=="external":
        for f in pii_fields:
            if output.get(f) not in (None,""):
                return False
    core_vals = core.get("values",{})
    for k,v in core_vals.items():
        if v is not None and k in output and output[k] != v:
            return False
    return True
