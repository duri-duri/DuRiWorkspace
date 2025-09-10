#!/usr/bin/env python3
import json, re, sys, argparse, pathlib, yaml

def load_rules(p):
    r = yaml.safe_load(open(p,'r',encoding='utf-8'))
    bans = [re.compile(re.escape(s)) for s in r.get('banned_phrases',[])]
    hr = [(re.compile(x['regex']), x['action']) for x in r.get('high_risk_triggers',[])]
    need_disclaimer = bool(r.get('disclaimer_required', False))
    pii = r.get('pii_guard', {})
    pii_detect = [re.compile(re.escape(s)) for s in pii.get('detect',[])]
    pii_action = pii.get('action','mask_or_block')
    return bans, hr, need_disclaimer, pii_detect, pii_action

def judge_one(text, bans, hr, need_disclaimer, pii_detect):
    risks=[]
    for rgx, act in hr:
        if rgx.search(text): risks.append(act)
    banned_hit = any(rgx.search(text) for rgx in bans)
    pii_hit = any(rgx.search(text) for rgx in pii_detect)
    # 간단한 매핑
    if 'advise_emergency' in risks: label='advise_emergency'
    elif '약' in text and '어지러움' in text: label='check_interaction'
    else: label='ok'
    return {
        "label": label,
        "banned_phrase": banned_hit,
        "pii_detected": pii_hit,
        "disclaimer_required": need_disclaimer
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--rules', required=True)
    ap.add_argument('--infile', required=True)
    ap.add_argument('--out', required=True)
    args=ap.parse_args()

    bans, hr, need_disc, pii_det, _ = load_rules(args.rules)
    total=0; passcnt=0; fails=[]
    with open(args.infile,'r',encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            total+=1
            obj=json.loads(line)
            res=judge_one(obj['input'], bans, hr, need_disc, pii_det)
            obj['pred']=res['label']
            ok = (obj.get('expect_risk')==obj['pred']) and not res['banned_phrase']
            passcnt += int(ok)
            if not ok: fails.append(obj)

    report={
        "total": total,
        "pass": passcnt,
        "pass_rate": (passcnt/total if total else 0.0),
        "fails": fails
    }
    pathlib.Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"[OK] med_smoke report -> {args.out}")
if __name__=="__main__": main()
