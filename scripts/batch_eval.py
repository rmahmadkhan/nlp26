#!/usr/bin/env python3
"""Gemini Batch API mode (50% price; paid tier only) for the same eval. Needs: pip install google-genai.

  python scripts/batch_eval.py submit --model gemini-3.5-flash-lite --scripts en ru ur --conds zs --thinking-level minimal --max-requests 3000
  python scripts/batch_eval.py status            # all jobs in batches/
  python scripts/batch_eval.py collect           # append finished jobs' results to results/<model>/<script>_<cond>.jsonl

Requests already present in the results file, or pending in an unfinished job, are not resubmitted.
Records are identical to run_eval.py's, plus batch_job and batch=True.
"""
import argparse, glob, json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_eval import build_prompt, parse_answer, ROOT
from google import genai
from google.genai import types

BDIR = os.path.join(ROOT, 'batches')


def load_items(args):
    items = [json.loads(l) for l in open(os.path.join(ROOT, 'data/subset_items.jsonl'))]
    uo = os.path.join(ROOT, 'data/options_ur.jsonl'); qf = os.path.join(ROOT, 'data/questions_ur_fixed.jsonl')
    if os.path.exists(uo):
        m = {j['uid']: j['options_ur'] for j in map(json.loads, open(uo))}
        for it in items:
            if it['uid'] in m: it['options_ur'] = m[it['uid']]
    fx = {j['uid']: j['question_ur_fixed'] for j in map(json.loads, open(qf))} if os.path.exists(qf) else {}
    for it in items:
        if it['uid'] in fx:
            it['question_ur'] = fx[it['uid']]; it['ur_question_fixed'] = True
        elif it.get('ur_truncated', it.get('ur_maybe_truncated')):
            it.pop('options_ur', None)  # never run a truncated Urdu question
    return items


def submit(args, client):
    items = load_items(args)
    mdir = os.path.join(ROOT, 'results', args.model)
    pending = set()
    for mf in glob.glob(os.path.join(BDIR, '*.json')):
        man = json.load(open(mf))
        if man['model'] == args.model and not man.get('collected'):
            pending |= set(man['keys'])
    reqs, keys = [], []
    for c in args.conds:
        for s in args.scripts:
            path = os.path.join(mdir, f'{s}_{c}.jsonl')
            done = {json.loads(l)['uid'] for l in open(path)} if os.path.exists(path) else set()
            for it in items:
                k = f'{s}|{c}|{it["uid"]}'
                if it['uid'] in done or k in pending or not it.get(f'options_{s}'):
                    continue
                cfg = {'temperature': args.temperature, 'max_output_tokens': args.max_tokens}
                if args.thinking_level:
                    cfg['thinking_config'] = {'thinking_level': args.thinking_level}
                reqs.append({'contents': [{'role': 'user', 'parts': [{'text': build_prompt(it, s, c)}]}],
                             'metadata': {'key': k}, 'config': cfg})
                keys.append(k)
    reqs, keys = reqs[:args.max_requests], keys[:args.max_requests]
    if not reqs:
        print('nothing to submit'); return
    job = client.batches.create(model=args.model, src=reqs,
                                config={'display_name': f'nlp-project-{args.model}-{dt.datetime.now():%m%d-%H%M}'})
    man = dict(job=job.name, model=args.model, keys=keys, temperature=args.temperature, thinking_level=args.thinking_level,
               created=dt.datetime.now(dt.timezone.utc).isoformat(), collected=False)
    json.dump(man, open(os.path.join(BDIR, job.name.replace('/', '_') + '.json'), 'w'))
    print('submitted', job.name, len(keys), 'requests')


def status(args, client):
    for mf in sorted(glob.glob(os.path.join(BDIR, '*.json'))):
        man = json.load(open(mf)); j = client.batches.get(name=man['job'])
        print(man['job'], man['model'], len(man['keys']), j.state, 'collected' if man.get('collected') else '', j.completion_stats)


def collect(args, client):
    items = {it['uid']: it for it in load_items(args)}
    for mf in sorted(glob.glob(os.path.join(BDIR, '*.json'))):
        man = json.load(open(mf))
        if man.get('collected'):
            continue
        j = client.batches.get(name=man['job'])
        if j.state.name != 'JOB_STATE_SUCCEEDED':
            print(man['job'], j.state.name); continue
        n_ok = n_err = 0
        mdir = os.path.join(ROOT, 'results', man['model']); os.makedirs(mdir, exist_ok=True)
        for ir in j.dest.inlined_responses:
            k = (ir.metadata or {}).get('key')
            s, c, uid = k.split('|'); it = items[uid]
            if ir.error or not ir.response:
                n_err += 1
                with open(os.path.join(BDIR, 'errors.jsonl'), 'a') as f:
                    f.write(json.dumps({'job': man['job'], 'key': k, 'error': str(ir.error)}) + '\n')
                continue
            r = ir.response
            cand = r.candidates[0] if r.candidates else None
            text = ''.join(p.text or '' for p in (cand.content.parts if cand and cand.content and cand.content.parts else []) if not p.thought)
            pred, how = parse_answer(text, it['options_en'].keys(), c)
            u = r.usage_metadata.model_dump(exclude_none=True, by_alias=True, mode='json') if r.usage_metadata else None
            rec = dict(uid=uid, source=it['source'], script=s, cond=c, gold=it['answer'], pred=pred, correct=pred == it['answer'],
                       parse=how, ur_question_fixed=it.get('ur_question_fixed', False) if s == 'ur' else None, response=text,
                       finish_reason=str(cand.finish_reason) if cand else None, model=man['model'], model_version=r.model_version,
                       response_id=r.response_id, usage=u, temperature=man['temperature'], thinking_level=man['thinking_level'],
                       thinking_budget=None, retries=0, prompt=build_prompt(it, s, c), batch=True, batch_job=man['job'],
                       t_start=man['created'], t_end=j.end_time.isoformat() if j.end_time else None)
            with open(os.path.join(mdir, f'{s}_{c}.jsonl'), 'a') as f:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            n_ok += 1
        man['collected'] = True; man['collected_ok'] = n_ok; man['collected_err'] = n_err
        json.dump(man, open(mf, 'w'))
        print(man['job'], 'collected', n_ok, 'errors', n_err, '(errored keys are resubmitted by the next submit)')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['submit', 'status', 'collect'])
    ap.add_argument('--model', default='gemini-3.5-flash-lite')
    ap.add_argument('--scripts', nargs='+', default=['en', 'ru', 'ur'])
    ap.add_argument('--conds', nargs='+', default=['zs'])
    ap.add_argument('--temperature', type=float, default=0.1)
    ap.add_argument('--max-tokens', type=int, default=4096)
    ap.add_argument('--thinking-level', default='minimal')
    ap.add_argument('--max-requests', type=int, default=3000)
    args = ap.parse_args()
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    {'submit': submit, 'status': status, 'collect': collect}[args.cmd](args, client)
