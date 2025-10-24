import json
import pathlib
import sys
import time

from DuRiCore.unified.reasoning.service import UnifiedReasoningService

outdir = pathlib.Path("var/reports/mirror")
outdir.mkdir(parents=True, exist_ok=True)
log = (outdir / "samples.jsonl").open("a", encoding="utf-8")

svc = UnifiedReasoningService()


def run_one(q):
    # 기본 경로(기존 엔진)
    base = svc.engine.process({"query": q})
    # 전략 경로(통합 – 기본/전략 둘 다 같은 엔진이면 결과 같을 수 있음)
    uni = svc.process({"query": q})
    agree = str(base.get("result")) == str(uni.get("result"))
    rec = {"ts": time.time(), "q": q, "base": base, "unified": uni, "agree": agree}
    log.write(json.dumps(rec, ensure_ascii=False) + "\n")
    log.flush()
    return agree


def main():
    data = sys.stdin.read().strip()
    obj = json.loads(data) if data else {}
    q = obj.get("query", "1+1")
    ok = run_one(q)
    print(json.dumps({"ok": ok}))


if __name__ == "__main__":
    main()
