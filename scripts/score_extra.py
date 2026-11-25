#!/usr/bin/env python3
"""Extra scoring for the small-model runs (complements scripts/score.py, which is unchanged):
paper-style accuracy table (2 decimals) with bootstrap 95% CIs, paired EN-RU / EN-UR / RU-UR gaps with exact
McNemar p, truncated-vs-complete Urdu split, compliance / parse-failure / length-cutoff rates, and the
U-MIRAGE paper's reference rows (all_configurations_accuracy.csv, full 7,663-item benchmark).

  python scripts/score_extra.py --models qwen3.5-0.8b-bnb4 llama3.2-1b-instruct-bnb4 llama3.2-1b-instruct-bf16
Writes results/<tag>/scores_extra_sample366.md per model and results/summary_small_models_sample366.md.
"""
import argparse, json, os, re, sys, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_eval import parse_answer, PARSER_VERSION
from score import boot_ci, mcnemar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONDS = [('zs', 'Zero-Shot'), ('umcot', 'CoT (U-MIRAGE prompt)')]
SCRIPTS = ['en', 'ru', 'ur']
# U-MIRAGE paper reference (umirage/all_configurations_accuracy.csv; full benchmark, "CoT" = their with_reasoning prompt)
PAPER_ALL = {  # U-MIRAGE all_configurations_accuracy.csv, full 7,663-item benchmark ("CoT" = their with_reasoning prompt)
    'GPT-5 nano [paper]':            {('en', 'zs'): .7962, ('en', 'umcot'): .7865, ('ru', 'zs'): .7502, ('ru', 'umcot'): .7498, ('ur', 'zs'): .7299, ('ur', 'umcot'): .7023},
    'Gemini 2.0 Flash-Lite [paper]': {('en', 'zs'): .7177, ('en', 'umcot'): .7779, ('ru', 'zs'): .6582, ('ru', 'umcot'): .7414, ('ur', 'zs'): .6768, ('ur', 'umcot'): .7013},
    'Gemma 2 2B [paper]':            {('en', 'zs'): .4198, ('en', 'umcot'): .4325, ('ru', 'zs'): .3247, ('ru', 'umcot'): .3500, ('ur', 'zs'): .3124, ('ur', 'umcot'): .3367},
    'Qwen 2.5 0.5B (q) [paper]':     {('en', 'zs'): .2592, ('en', 'umcot'): .2974, ('ru', 'zs'): .2378, ('ru', 'umcot'): .2765, ('ur', 'zs'): .2305, ('ur', 'umcot'): .2721},
    'LLaMA 3.2 1B (q) [paper]':      {('en', 'zs'): .1886, ('en', 'umcot'): .3889, ('ru', 'zs'): .1982, ('ru', 'umcot'): .2400, ('ur', 'zs'): .1883, ('ur', 'umcot'): .1781},
    'LLaMA 3.2 1B [paper]':          {('en', 'zs'): .4549, ('en', 'umcot'): .4437, ('ru', 'zs'): .3448, ('ru', 'umcot'): .3616, ('ur', 'zs'): .3364, ('ur', 'umcot'): .3124},
}
PAPER_SETS = {'small': ['Qwen 2.5 0.5B (q) [paper]', 'LLaMA 3.2 1B (q) [paper]', 'LLaMA 3.2 1B [paper]'],
              'api': ['GPT-5 nano [paper]', 'Gemini 2.0 Flash-Lite [paper]', 'Gemma 2 2B [paper]'],
              'all': list(PAPER_ALL)}
# which U-MIRAGE paper row each of our runs succeeds (for the side-by-side table)
SUCCESSOR_OF = {'gpt-6-luna': 'GPT-5 nano [paper]', 'gemini-3.5-flash-lite': 'Gemini 2.0 Flash-Lite [paper]',
                'gemma-4-26b-a4b-it': 'Gemma 2 2B [paper]', 'qwen3.5-0.8b-bnb4': 'Qwen 2.5 0.5B (q) [paper]',
                'llama3.2-1b-instruct-bnb4': 'LLaMA 3.2 1B (q) [paper]', 'llama3.2-1b-instruct-bf16': 'LLaMA 3.2 1B [paper]'}


def load(mdir, keep):
    R = {}
    for s in SCRIPTS:
        for c, _ in CONDS:
            f = os.path.join(mdir, f'{s}_{c}.jsonl')
            if not os.path.exists(f):
                continue
            recs = {}
            for l in open(f):
                if not l.strip():
                    continue
                r = json.loads(l)
                if keep and r['uid'] not in keep:
                    continue
                r['pred'], r['parse'] = parse_answer(r['response'], 'ABCD' if r['gold'] in 'ABCD' else r['gold'], r['cond'])
                r['correct'] = r['pred'] == r['gold']
                recs[r['uid']] = r
            R[(s, c)] = recs
    return R


def paired(R, a, b, c, ids=None):
    if (a, c) not in R or (b, c) not in R:
        return None
    common = set(R[(a, c)]) & set(R[(b, c)])
    if ids is not None:
        common &= ids
    common = sorted(common)
    if len(common) < 2:
        return None
    x = np.array([R[(a, c)][i]['correct'] for i in common], int); y = np.array([R[(b, c)][i]['correct'] for i in common], int)
    lo, hi = boot_ci(x - y); b01, b10, p = mcnemar(x, y)
    return len(common), x.mean(), y.mean(), (x - y).mean(), lo, hi, b01, b10, p


def score_extra_main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--models', nargs='+', required=True)
    ap.add_argument('--labels', nargs='*', default=None, help='display names, same order as --models')
    ap.add_argument('--outdir', default=os.path.join(ROOT, 'results'))
    ap.add_argument('--items', default=os.path.join(ROOT, 'share/nlp_project_sample366.jsonl'))
    ap.add_argument('--ids', default=os.path.join(ROOT, 'data/sample366_ids.csv'))
    ap.add_argument('--paper-rows', choices=list(PAPER_SETS), default='small')
    ap.add_argument('--summary-name', default='summary_small_models_sample366.md')
    ap.add_argument('--title', default='Small-model successors on the 366-item sample')
    args = ap.parse_args(argv)
    items = {j['uid']: j for j in map(json.loads, open(args.items))}
    keep = {r['uid'] for r in csv.DictReader(open(args.ids))} if args.ids and os.path.exists(args.ids) else set(items)
    trunc = {u for u, j in items.items() if j.get('ur_question_truncated_in_original', j.get('ur_truncated'))}
    labels = args.labels or args.models
    summary = [f'# {args.title} (parser v{PARSER_VERSION})\n',
               '## Paper-style accuracy table (fraction correct, 2 decimals; n per cell in the per-model files)\n',
               '| Model | EN Zero-Shot | EN CoT | RU Zero-Shot | RU CoT | UR Zero-Shot | UR CoT |', '|---|---|---|---|---|---|---|']
    gaps_rows, trunc_rows, comp_rows, pct_rows, pct_of = [], [], [], [], {}
    for tag, lab in zip(args.models, labels):
        mdir = os.path.join(args.outdir, tag)
        R = load(mdir, keep)
        out = [f'# Extra scores for {lab} ({tag}), parser v{PARSER_VERSION}\n',
               '| script | cond | n | accuracy | 95% bootstrap CI | parse fail | zs not bare letter | hit max_tokens |', '|---|---|---|---|---|---|---|---|']
        cells = []
        for s in SCRIPTS:
            for c, _ in CONDS:
                v = list(R.get((s, c), {}).values())
                if not v:
                    cells.append('-'); continue
                x = np.array([r['correct'] for r in v], float)
                rng = np.random.default_rng(0); bs = x[rng.integers(0, len(x), size=(10000, len(x)))].mean(1)
                lo, hi = np.percentile(bs, [2.5, 97.5])
                pf = sum(r['pred'] is None for r in v)
                nb = sum(len(re.sub(r'[\s\*\.\(\)]', '', r['response'] or '')) > 1 for r in v) if c == 'zs' else None
                ln = sum(r.get('finish_reason') in ('length', 'MAX_TOKENS') for r in v)
                out.append(f'| {s} | {c} | {len(v)} | {x.mean():.2f} | [{lo:.2f}, {hi:.2f}] | {pf} ({100*pf/len(v):.1f}%) | '
                           f'{"-" if nb is None else f"{nb} ({100*nb/len(v):.1f}%)"} | {ln} ({100*ln/len(v):.1f}%) |')
                cells.append(f'{x.mean():.2f}' + ('' if len(v) == len(keep) else f' (n={len(v)})'))
                comp_rows.append(f'| {lab} | {s}/{c} | {len(v)} | {pf} ({100*pf/len(v):.1f}%) | {"-" if nb is None else f"{100*nb/len(v):.1f}%"} | {100*ln/len(v):.1f}% |')
        summary.append(f'| {lab} | ' + ' | '.join(cells) + ' |')
        pct_of[tag] = [f'{100*np.mean([r["correct"] for r in R[(s, c)].values()]):.2f}' if R.get((s, c)) else '-' for s in SCRIPTS for c, _ in CONDS]
        pct_rows.append(f'| {lab} | ' + ' | '.join(pct_of[tag]) + ' |')
        out += ['\n## Paired gaps (accuracy in %, diff = first - second in percentage points; bootstrap 10k; exact McNemar)\n',
                '| cond | pair | n | acc 1st | acc 2nd | diff | 95% CI | b01/b10 | p |', '|---|---|---|---|---|---|---|---|---|']
        for c, cn in CONDS:
            for a, b in [('en', 'ru'), ('en', 'ur'), ('ru', 'ur')]:
                g = paired(R, a, b, c)
                if g:
                    n, xa, xb, d, lo, hi, b01, b10, p = g
                    row = f'| {c} | {a.upper()}-{b.upper()} | {n} | {100*xa:.2f} | {100*xb:.2f} | {100*d:+.2f} | [{100*lo:+.2f}, {100*hi:+.2f}] | {b01}/{b10} | {p:.3g} |'
                    out.append(row); gaps_rows.append(f'| {lab} ' + row)
        out += ['\n## Urdu: questions truncated in the released U-MIRAGE CSV vs complete (original questions used)\n',
                '| cond | subset | n | UR acc | EN acc (same items) | EN-UR | 95% CI | McNemar p |', '|---|---|---|---|---|---|---|---|']
        for c, cn in CONDS:
            for nm, ids in [('truncated', trunc & keep), ('complete', keep - trunc)]:
                g = paired(R, 'en', 'ur', c, ids)
                if g:
                    n, xa, xb, d, lo, hi, b01, b10, p = g
                    row = f'| {c} | {nm} | {n} | {100*xb:.2f} | {100*xa:.2f} | {100*d:+.2f} | [{100*lo:+.2f}, {100*hi:+.2f}] | {p:.3g} |'
                    out.append(row); trunc_rows.append(f'| {lab} ' + row)
        txt = '\n'.join(out) + '\n'
        open(os.path.join(mdir, 'scores_extra_sample366.md'), 'w').write(txt)
        print(txt)
    summary.append('| *U-MIRAGE paper reference rows (full benchmark, 7,663 items):* | | | | | | |')
    for lab in PAPER_SETS[args.paper_rows]:
        d = PAPER_ALL[lab]
        summary.append(f'| {lab} | ' + ' | '.join(f'{d[(s, c)]:.2f}' for s in SCRIPTS for c, _ in CONDS) + ' |')
    summary += ['\n## Accuracy in % (2 decimals)\n', '| Model | EN ZS | EN CoT | RU ZS | RU CoT | UR ZS | UR CoT |', '|---|---|---|---|---|---|---|'] + pct_rows
    pairs = [(SUCCESSOR_OF[t], t, lab) for t, lab in zip(args.models, labels) if SUCCESSOR_OF.get(t) in PAPER_SETS[args.paper_rows]]
    order = list(PAPER_ALL)
    pairs.sort(key=lambda x: order.index(x[0]))
    if pairs:
        summary += ['\n## Paper rows vs our successors (accuracy in %, 2 decimals; each paper row directly above its successor)\n',
                    'Paper = U-MIRAGE, full benchmark (7,663 items). Ours = a random 366-item sample (seed 42), so the rows are not item-matched. '
                    'Gemma 4 26B-A4B is not size-matched to Gemma 2 2B (26B total / ~4B active parameters vs 2B).\n',
                    '| Model | EN ZS | EN CoT | RU ZS | RU CoT | UR ZS | UR CoT |', '|---|---|---|---|---|---|---|']
        for prow, t, lab in pairs:
            summary.append(f'| {prow.replace(" [paper]", "")} [paper] | ' + ' | '.join(f'{100*PAPER_ALL[prow][(s, c)]:.2f}' for s in SCRIPTS for c, _ in CONDS) + ' |')
            summary.append(f'| {lab} [ours] | ' + ' | '.join(pct_of[t]) + ' |')
    summary += ['\n## Paired gaps (accuracy %, diff in pp)\n', '| model | cond | pair | n | acc 1st | acc 2nd | diff | 95% CI | b01/b10 | McNemar p |',
                '|---|---|---|---|---|---|---|---|---|---|'] + gaps_rows
    summary += ['\n## Truncated vs complete Urdu questions (accuracy %, diff in pp)\n', '| model | cond | subset | n | UR acc | EN acc | EN-UR | 95% CI | McNemar p |',
                '|---|---|---|---|---|---|---|---|---|'] + trunc_rows
    summary += ['\n## Compliance\n', '| model | run | n | parse fail | zs not bare letter | hit max_tokens |', '|---|---|---|---|---|---|'] + comp_rows
    txt = '\n'.join(summary) + '\n'
    open(os.path.join(args.outdir, args.summary_name), 'w').write(txt)
    print(txt)


if __name__ == '__main__':
    score_extra_main()
