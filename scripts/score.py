#!/usr/bin/env python3
"""Score results/<model>/*.jsonl: accuracy, paired gaps with bootstrap CIs, exact McNemar, per-source,
parse failures, reply-script detection.  python scripts/score.py --model gemini-4-hydrogen"""
import argparse, glob, json, os, re
import numpy as np, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_eval import parse_answer, PARSER_VERSION
from scipy.stats import binomtest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RU_WORDS = set('hai hain ka ki ke mein se aur nahi nahin kya yeh ye woh wo ko ho hota hoti hote jata jati liye bhi tha thi sakta sakti kar karta karti par lekin kyunke kyun agar jo ek sab zyada kam wala wali'.split())
EN_WORDS = set('the is are of and to in that with for this which it be as by on not or an was'.split())


def reply_script(text):
    t = re.sub(r'(?im)^\s*answer\s*:.*$', '', text or '')
    ar = len(re.findall(r'[\u0600-\u06FF]', t)); la = len(re.findall(r'[A-Za-z]', t))
    if ar + la == 0:
        return 'none'
    if ar / (ar + la) > 0.5:
        return 'ur'
    w = re.findall(r'[a-z]+', t.lower())
    ru, en = sum(x in RU_WORDS for x in w), sum(x in EN_WORDS for x in w)
    return 'ru' if ru > en else 'en'


def boot_ci(diff, B=10000, seed=0):
    rng = np.random.default_rng(seed); n = len(diff)
    m = diff[rng.integers(0, n, size=(B, n))].mean(1)
    return np.percentile(m, [2.5, 97.5])


def mcnemar(a, b):
    b01, b10 = int(((a == 1) & (b == 0)).sum()), int(((a == 0) & (b == 1)).sum())
    p = binomtest(b01, b01 + b10, 0.5).pvalue if b01 + b10 else 1.0
    return b01, b10, p


def score_main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('--model', required=True)
    ap.add_argument('--ids', default=None, help='csv with a uid column: score only these items')
    ap.add_argument('--outdir', default=os.path.join(ROOT, 'results'))
    args = ap.parse_args(argv)
    mdir = os.path.join(args.outdir, args.model.replace('/', '_'))
    SUBSRC = {j['uid']: j['source'] for j in map(json.loads, open(os.path.join(ROOT, 'data/subset_items.jsonl')))}
    VALID = {j['uid']: sorted(j['options_en']) for j in map(json.loads, open(os.path.join(ROOT, 'data/subset_items.jsonl')))}
    KEEP = None
    if args.ids:
        import csv
        KEEP = {r['uid'] for r in csv.DictReader(open(args.ids))}
        SUBSRC = {u: v for u, v in SUBSRC.items() if u in KEEP}
    R = {}
    for f in sorted(glob.glob(os.path.join(mdir, '*_*.jsonl'))):
        s, c = os.path.basename(f)[:-6].split('_', 1)
        recs = {}
        for l in open(f):
            r = json.loads(l)
            valid = VALID.get(r['uid']) or 'ABCD'  # re-parse raw reply with current parser
            r['pred'], r['parse'] = parse_answer(r['response'], valid, r['cond']); r['correct'] = r['pred'] == r['gold']
            if KEEP is None or r['uid'] in KEEP:
                recs[r['uid']] = r  # last write wins
        R[(s, c)] = recs
    out = [f'# Scores for {args.model} (answers re-parsed from raw replies, parser v{PARSER_VERSION})\n']
    out.append('| script | cond | n | accuracy | source-weighted acc* | parse fail | zs non-compliant (not a bare letter) | mean in tok | mean out tok (visible+thinking) |\n|---|---|---|---|---|---|---|---|---|')
    for (s, c), recs in sorted(R.items()):
        v = list(recs.values()); n = len(v)
        acc = np.mean([r['correct'] for r in v]); pf = sum(r['pred'] is None for r in v)
        ui = np.mean([(r['usage'] or {}).get('promptTokenCount', (r['usage'] or {}).get('prompt_tokens', 0)) for r in v])
        uo = np.mean([(r['usage'] or {}).get('candidatesTokenCount', 0) + (r['usage'] or {}).get('thoughtsTokenCount', 0)
                      + (r['usage'] or {}).get('completion_tokens', 0) for r in v])  # OpenAI usage keys too
        nc = sum(len(re.sub(r'[\s\*\.\(\)]', '', r['response'] or '')) > 1 for r in v) if c == 'zs' else None
        nc_s = f'{nc} ({100*nc/n:.1f}%)' if nc is not None else '-'
        W = {so: sum(1 for x in SUBSRC.values() if x == so) / len(SUBSRC) for so in set(SUBSRC.values())}
        per = {so: np.mean([r['correct'] for r in v if r['source'] == so]) for so in W if sum(r['source'] == so for r in v) >= 10}
        wacc = sum(W[so] * a for so, a in per.items()) / sum(W[so] for so in per) if per else float('nan')
        out.append(f'| {s} | {c} | {n} | {100*acc:.1f} | {100*wacc:.1f} | {pf} ({100*pf/n:.1f}%) | {nc_s} | {ui:.0f} | {uo:.0f} |')
    out.append('\n*re-weighted to the subset source mix (over sources with >=10 items done), to offset processing-order imbalance.')
    out.append('\n## Paired comparisons (items answered in both; diff = first - second, pp)\n')
    out.append('| cond | pair | n paired | acc 1st | acc 2nd | diff | 95% bootstrap CI (10k) | b01/b10 | McNemar exact p |\n|---|---|---|---|---|---|---|---|---|')
    for c in sorted({c for _, c in R}):
        for a, b in [('en', 'ur'), ('en', 'ru'), ('ru', 'ur')]:
            if (a, c) not in R or (b, c) not in R:
                continue
            ids = sorted(set(R[(a, c)]) & set(R[(b, c)]))
            if len(ids) < 2:
                continue
            x = np.array([R[(a, c)][i]['correct'] for i in ids], int); y = np.array([R[(b, c)][i]['correct'] for i in ids], int)
            lo, hi = boot_ci(x - y); b01, b10, p = mcnemar(x, y)
            out.append(f'| {c} | {a.upper()}-{b.upper()} | {len(ids)} | {100*x.mean():.1f} | {100*y.mean():.1f} | {100*(x-y).mean():+.1f} | [{100*lo:+.1f}, {100*hi:+.1f}] | {b01}/{b10} | {p:.3g} |')
    out.append('\n## Accuracy by source dataset (%; n in brackets)\n')
    srcs = sorted({r['source'] for recs in R.values() for r in recs.values()})
    out.append('| script/cond | ' + ' | '.join(srcs) + ' |\n|---|' + '---|' * len(srcs))
    for (s, c), recs in sorted(R.items()):
        cells = []
        for so in srcs:
            v = [r['correct'] for r in recs.values() if r['source'] == so]
            cells.append(f'{100*np.mean(v):.1f} [{len(v)}]' if v else '-')
        out.append(f'| {s}/{c} | ' + ' | '.join(cells) + ' |')
    cot = [(k, v) for k, v in R.items() if k[1] in ('cot', 'umcot')]
    if cot:
        out.append('\n## Reply script for reasoning outputs (heuristic: Arabic-script share; Roman Urdu vs English by function words)\n')
        out.append('| asked | n | replied en | replied ru | replied ur | % in asked script |\n|---|---|---|---|---|---|')
        for (s, c), recs in sorted(cot):
            sc = [reply_script(r['response']) for r in recs.values()]; n = len(sc)
            out.append(f'| {s}/{c} | {n} | {sc.count("en")} | {sc.count("ru")} | {sc.count("ur")} | {100*sc.count(s)/n:.0f}% |')
    txt = '\n'.join(out) + '\n'
    open(os.path.join(mdir, 'scores' + ('_' + os.path.basename(args.ids).split('_')[0] if args.ids else '') + '.md'), 'w').write(txt); print(txt)


if __name__ == '__main__':
    score_main()
