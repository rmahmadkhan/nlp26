#!/usr/bin/env python3
"""One-click check: regenerate every results table from the included raw model outputs (no API keys, no network)
and assert the numbers match the reported ones in expected_results.json.

  python scripts/reproduce_tables.py            # regenerate + verify (exit code 0 = all match)
  python scripts/reproduce_tables.py --write-expected   # (maintainers) refresh expected_results.json
"""
import argparse, contextlib, io, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from run_eval import parse_answer, PARSER_VERSION
from score import mcnemar, score_main
from score_extra import score_extra_main

REPRO_API = {'gpt-6-luna': 'GPT-6 Luna', 'gemma-4-26b-a4b-it': 'Gemma 4 26B-A4B', 'gemini-3.5-flash-lite': 'Gemini 3.5 Flash-Lite'}
REPRO_SMALL = {'qwen3.5-0.8b-bnb4': 'Qwen3.5 0.8B (q, NF4)', 'llama3.2-1b-instruct-bnb4': 'Llama 3.2 1B Instruct (q, NF4)',
               'llama3.2-1b-instruct-bf16': 'Llama 3.2 1B Instruct (bf16)'}
REPRO_MODELS = {**REPRO_API, **REPRO_SMALL}  # all six models
REPRO_SCRIPTS, REPRO_CONDS = ['en', 'ru', 'ur'], ['zs', 'umcot']


def metrics(rdir):
    items = {j['uid']: j for j in map(json.loads, open(os.path.join(ROOT, 'share/nlp_project_sample366.jsonl')))}
    trunc = {u for u, j in items.items() if j.get('ur_question_truncated_in_original')}
    out = {'parser_version': PARSER_VERSION, 'models': {}}
    for m in REPRO_MODELS:
        R = {}
        for s in REPRO_SCRIPTS:
            for c in REPRO_CONDS:
                recs = {}
                for l in open(os.path.join(rdir, m, f'{s}_{c}.jsonl')):
                    r = json.loads(l)
                    if r['uid'] in items:
                        pred, _ = parse_answer(r['response'], 'ABCD', r['cond'])
                        recs[r['uid']] = (pred == r['gold'], pred is None)
                R[(s, c)] = recs
        mm = {'accuracy_pct': {}, 'n': {}, 'parse_fail': {}, 'gaps': {}, 'ur_truncation_split': {}}
        for (s, c), recs in R.items():
            mm['n'][f'{s}_{c}'] = len(recs)
            mm['accuracy_pct'][f'{s}_{c}'] = round(100 * np.mean([v[0] for v in recs.values()]), 2)
            mm['parse_fail'][f'{s}_{c}'] = int(sum(v[1] for v in recs.values()))
        for c in REPRO_CONDS:
            for a, b in [('en', 'ru'), ('en', 'ur'), ('ru', 'ur')]:
                ids = sorted(set(R[(a, c)]) & set(R[(b, c)]))
                x = np.array([R[(a, c)][i][0] for i in ids], int); y = np.array([R[(b, c)][i][0] for i in ids], int)
                b01, b10, p = mcnemar(x, y)
                mm['gaps'][f'{c}_{a}-{b}'] = {'n': len(ids), 'diff_pp': round(100 * (x - y).mean(), 2), 'b01': b01, 'b10': b10, 'mcnemar_p': float(f'{p:.4g}')}
            for nm, sub in [('truncated', trunc), ('complete', set(items) - trunc)]:
                ids = sorted(set(R[('ur', c)]) & sub)
                mm['ur_truncation_split'][f'{c}_{nm}'] = {'n': len(ids), 'ur_acc_pct': round(100 * np.mean([R[('ur', c)][i][0] for i in ids]), 2),
                                                          'en_acc_pct': round(100 * np.mean([R[('en', c)][i][0] for i in ids]), 2)}
        out['models'][m] = mm
    return out


def compare(a, b, path=''):
    bad = []
    if isinstance(a, dict):
        for k in set(a) | set(b):
            if k not in a or k not in b:
                bad.append(f'{path}/{k}: missing'); continue
            bad += compare(a[k], b[k], f'{path}/{k}')
    elif isinstance(a, float) or isinstance(b, float):
        if not np.isclose(a, b, rtol=1e-3, atol=1e-9):
            bad.append(f'{path}: got {a}, expected {b}')
    elif a != b:
        bad.append(f'{path}: got {a}, expected {b}')
    return bad


def reproduce_main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', default=os.path.join(ROOT, 'results'))
    ap.add_argument('--write-expected', action='store_true')
    args = ap.parse_args(argv)
    # 1) regenerate the markdown tables with the project's scorers
    with contextlib.redirect_stdout(io.StringIO()):  # the scorers print their tables; keep this check's output short
        for m in REPRO_MODELS:
            score_main(['--model', m, '--outdir', args.results, '--ids', os.path.join(ROOT, 'data/sample366_ids.csv')])
        for group, rows, name, title in [(REPRO_API, 'api', 'summary_api_models_sample366.md', 'API models on the 366-item sample'),
                                         (REPRO_SMALL, 'small', 'summary_small_models_sample366.md', 'Small-model successors on the 366-item sample'),
                                         (REPRO_MODELS, 'all', 'summary_all_models_sample366.md', 'All six models on the 366-item sample')]:
            score_extra_main(['--outdir', args.results, '--models', *group, '--labels', *group.values(), '--paper-rows', rows,
                              '--summary-name', name, '--title', title])
    print('regenerated: results/<model>/scores_sample366.md, results/<model>/scores_extra_sample366.md (6 models), '
          'results/summary_{api,small,all}_models_sample366.md')
    # 2) recompute key numbers independently and compare with the reported values
    got = metrics(args.results)
    exp_path = os.path.join(ROOT, 'expected_results.json')
    if args.write_expected:
        json.dump(got, open(exp_path, 'w'), indent=1); print('wrote', exp_path); return
    bad = compare(got, json.load(open(exp_path)))
    print('\nAccuracy (%)                   ' + '  '.join(f'{s.upper()}-{c:<5}' for s in REPRO_SCRIPTS for c in REPRO_CONDS))
    for m, lab in REPRO_MODELS.items():
        print(f'{lab:<31}' + '  '.join(f'{got["models"][m]["accuracy_pct"][f"{s}_{c}"]:>8.2f}' for s in REPRO_SCRIPTS for c in REPRO_CONDS))
    if bad:
        print(f'\nFAIL: {len(bad)} mismatches'); [print('  ', b) for b in bad[:50]]; sys.exit(1)
    print(f'\nPASS: all reproduced numbers match expected_results.json (accuracies, n, parse failures, gaps, McNemar counts/p, truncation split)')


if __name__ == '__main__':
    reproduce_main()
