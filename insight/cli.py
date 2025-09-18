import argparse, sys, json, pathlib
from typing import List
from .engine import rank

def load_candidates(args: argparse.Namespace) -> List[str]:
    cands: List[str] = []
    for c in args.c or []:
        cands.append(c)
    for fp in args.c_file or []:
        p = pathlib.Path(fp)
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line: cands.append(line)
    return cands

def main(argv=None) -> int:
    ap = argparse.ArgumentParser("insight-cli")
    ap.add_argument("--prompt", required=True, help="prompt text")
    ap.add_argument("--c", action="append", dest="c", help="candidate text (repeatable)")
    ap.add_argument("--c-file", action="append", dest="c_file", help="file with one candidate per line")
    ap.add_argument("--topk", type=int, default=1)
    ap.add_argument("--json", action="store_true", help="print json")
    args = ap.parse_args(argv)
    C = load_candidates(args)
    if not C:
        print("no candidates", file=sys.stderr)
        return 2
    top = rank(args.prompt, C, k=args.topk)
    if args.json:
        out = [{"index": i, "score": s, **br} for (i, s, br) in top]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for (i, s, br) in top:
            print(f"#{i}  S={s:.3f}  novelty={br['novelty']:.3f}  coherence={br['coherence']:.3f}  brevity={br['brevity']:.3f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
