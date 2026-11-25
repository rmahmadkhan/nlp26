#!/usr/bin/env python3
"""Resumable runner for the NLP project RQ1 replication (U-MIRAGE prompts).

  python scripts/run_eval.py --provider gemini --model gemini-4-hydrogen --scripts en ru --conds zs --rpm 5
  python scripts/run_eval.py --provider openai --base-url https://api.openai.com/v1 --model gpt-5-nano ...
  (openai provider works with any OpenAI-compatible server: vLLM, Ollama, Together, OpenRouter, HF TGI)

Appends one JSON line per call to results/<model>/<script>_<cond>.jsonl and skips uids already done,
so it can be killed and restarted at any time. Only successful API calls are written; failed calls
are retried with backoff. A daily-quota 429 stops the run cleanly.
"""
import argparse, glob, json, os, random, re, sys, time, datetime as dt
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG = {'en': 'English', 'ru': 'Roman Urdu', 'ur': 'Urdu'}

# U-MIRAGE Figure 1, verbatim wording.
ZS = ("This is a medical multiple-choice question written in {language}\n"
      "Question: {question}\nOptions: {options}\n"
      "Select the single correct option (A, B, C, D). Only return the letter corresponding to the correct answer. No explanation.")
# U-MIRAGE's own "CoT" prompt (kept for reference; it forbids written reasoning). Use --conds umcot to run it.
UMCOT = ("This is a medical multiple-choice question written in {language}\n"
         "Question: {question}\nOptions: {options}\n"
         "Let's think step-by-step to reason about the correct answer based on medical knowledge. After reasoning, "
         "select the single best option (A, B, C, or D). Return only the final answer letter (A, B, C, or D) without any explanation.")
# Our written-CoT condition: same frame, reasoning is written out, answer on the last line.
COT = ("This is a medical multiple-choice question written in {language}\n"
       "Question: {question}\nOptions: {options}\n"
       "Let's think step-by-step to reason about the correct answer based on medical knowledge. Write out your reasoning, "
       "then select the single best option (A, B, C, or D). End your reply with a final line of the form 'Answer: X', "
       "where X is the option letter.")
TEMPLATES = {'zs': ZS, 'cot': COT, 'umcot': UMCOT}


def fmt_options(opts):
    return '\n'.join(f'{k}: {v}' for k, v in sorted(opts.items()))


def build_prompt(item, script, cond):
    q = item[f'question_{script}']
    opts = item.get(f'options_{script}')
    if opts is None:
        raise KeyError(f'no options_{script}')
    return TEMPLATES[cond].format(language=LANG[script], question=q, options=fmt_options(opts))


# ---------------------------------------------------------------- answer parsing
PARSER_VERSION = 2
UR_LETTER = {'ا': 'A', 'اے': 'A', 'بی': 'B', 'ب': 'B', 'سی': 'C', 'ڈی': 'D', 'د': 'D'}

def parse_answer(text, valid, cond):
    """Return (letter or None, method)."""
    if not text:
        return None, 'empty'
    t = text.strip()
    valid = set(valid)
    pats = [r'(?:final\s+)?answer\s*(?:is)?\s*[:：\-]?\s*\**\(?([A-D])\)?\b',
            r'(?:jawab|javab|جواب)\s*[:：\-]?\s*\**\(?([A-D])\)?\b']
    if cond in ('cot', 'umcot'):
        lines = [l for l in t.splitlines() if l.strip()]
        last = lines[-1] if lines else ''
        for p in pats:
            m = re.search(p, last, re.I)
            if m and m.group(1).upper() in valid:
                return m.group(1).upper(), 'last_line'
        for p in pats:
            ms = list(re.finditer(p, t, re.I))
            if ms and ms[-1].group(1).upper() in valid:
                return ms[-1].group(1).upper(), 'answer_anywhere'
    core = re.sub(r'[\s\*\.\)\(:"`\'\[\]]', '', t)
    if len(core) > 1:  # model ignored 'only the letter': look at the final line, then explicit conclusions
        lines = [l for l in t.splitlines() if l.strip()]
        last_letters = set(re.findall(r'(?<![A-Za-z])([A-D])(?![A-Za-z])', lines[-1])) if lines else set()
        if len(last_letters) == 1 and next(iter(last_letters)) in valid:
            return last_letters.pop(), 'last_line_letter'
        concl = r"(?:correct\s+(?:option|answer|choice)\s+is|answer\s+is|let'?s\s+(?:output|select|choose|go\s+with)|i\s+(?:choose|select)|best\s+(?:option|answer)\s+is)\s*[:\-]?\s*\**\s*(?:option\s*)?\(?([A-D])\)?(?![A-Za-z])"
        ms = [m for m in re.finditer(concl, t, re.I) if m.group(1).upper() in valid]
        if ms:
            return ms[-1].group(1).upper(), 'conclusion_phrase'
    if core.upper() in valid and len(core) == 1:
        return core.upper(), 'bare_letter'
    m = re.match(r'^\W*(?:option\s*)?([A-D])\b', t, re.I)
    if m and m.group(1).upper() in valid and (len(t) < 40 or cond == 'zs'):
        return m.group(1).upper(), 'leading_letter'
    for p in pats:
        ms = list(re.finditer(p, t, re.I))
        if ms and ms[-1].group(1).upper() in valid:
            return ms[-1].group(1).upper(), 'answer_anywhere'
    if core in UR_LETTER and UR_LETTER[core] in valid:
        return UR_LETTER[core], 'urdu_letter'
    if cond == 'zs':
        letters = set(re.findall(r'\b([A-D])\b', t))
        if len(letters) == 1 and next(iter(letters)) in valid:
            return letters.pop(), 'single_letter_in_text'
    return None, 'unparsed'


# ---------------------------------------------------------------- providers
class QuotaExhausted(Exception):
    pass


def call_gemini(args, prompt):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{args.model}:generateContent'
    gc = {'temperature': args.temperature, 'maxOutputTokens': args.max_tokens}
    if args.thinking_level:
        gc['thinkingConfig'] = {'thinkingLevel': args.thinking_level}
    elif args.thinking_budget is not None:
        gc['thinkingConfig'] = {'thinkingBudget': args.thinking_budget}
    body = {'contents': [{'role': 'user', 'parts': [{'text': prompt}]}], 'generationConfig': gc}
    r = requests.post(url, json=body, timeout=args.timeout,
                      headers={'x-goog-api-key': os.environ['GEMINI_API_KEY'], 'Content-Type': 'application/json'})
    d = r.json() if r.headers.get('content-type', '').startswith('application/json') else {'raw': r.text[:500]}
    if r.status_code != 200:
        return None, r.status_code, d
    cand = (d.get('candidates') or [{}])[0]
    parts = cand.get('content', {}).get('parts', [])
    text = ''.join(p.get('text', '') for p in parts if not p.get('thought'))
    return dict(text=text, finish_reason=cand.get('finishReason'), model_version=d.get('modelVersion'),
                response_id=d.get('responseId'), usage=d.get('usageMetadata')), 200, d


def call_openai(args, prompt):
    url = args.base_url.rstrip('/') + '/chat/completions'
    body = {'model': args.model, 'messages': [{'role': 'user', 'content': prompt}]}
    if not args.no_temperature:
        body['temperature'] = args.temperature
    body[args.max_tokens_param] = args.max_tokens
    if args.reasoning_effort:
        body['reasoning_effort'] = args.reasoning_effort
    key = os.environ.get(args.api_key_env, '')
    r = requests.post(url, json=body, timeout=args.timeout,
                      headers={'Authorization': f'Bearer {key}'} if key else {})
    try:
        d = r.json()
    except Exception:
        d = {'raw': r.text[:500]}
    if r.status_code != 200:
        return None, r.status_code, d
    ch = d['choices'][0]
    return dict(text=ch['message'].get('content') or '', finish_reason=ch.get('finish_reason'),
                model_version=d.get('model'), response_id=d.get('id'), usage=d.get('usage'),
                system_fingerprint=d.get('system_fingerprint'), service_tier=d.get('service_tier'),
                refusal=ch['message'].get('refusal')), 200, d


def retry_seconds(err):
    try:
        for det in err['error'].get('details', []):
            if det.get('@type', '').endswith('RetryInfo'):
                return float(det['retryDelay'].rstrip('s'))
    except Exception:
        pass
    return None


def is_daily(err):
    try:
        for det in err['error'].get('details', []):
            for v in det.get('violations', []):
                if 'PerDay' in v.get('quotaId', ''):
                    return True
    except Exception:
        pass
    return False


def call_with_retry(args, prompt):
    fn = call_gemini if args.provider == 'gemini' else call_openai
    delay = 5
    errors = []
    for attempt in range(args.max_retries):
        try:
            out, code, raw = fn(args, prompt)
        except requests.RequestException as e:
            out, code, raw = None, -1, {'exc': str(e)}
        if out is not None:
            out['errors'] = errors
            return out, attempt
        if code == 429 and is_daily(raw):
            with open(os.path.join(ROOT, 'quota_errors.log'), 'a') as qf:
                qf.write(dt.datetime.now(dt.timezone.utc).isoformat() + ' ' + json.dumps(raw) + '\n')
            raise QuotaExhausted(json.dumps(raw)[:600])
        if code == 402:
            raise QuotaExhausted('HTTP 402 (billing/prepayment): ' + json.dumps(raw)[:400])
        if code in (400, 401, 403, 404):
            raise SystemExit(f'non-retryable HTTP {code}: {json.dumps(raw)[:400]}')
        errors.append({'t': dt.datetime.now(dt.timezone.utc).isoformat(), 'code': code, 'body': json.dumps(raw)[:300]})
        wait = retry_seconds(raw) if code == 429 else None
        wait = max(wait or delay, 1) + random.uniform(0, 2)
        print(f'  [{code}] retry {attempt + 1}/{args.max_retries} in {wait:.0f}s: {json.dumps(raw)[:160]}', flush=True)
        time.sleep(wait)
        delay = min(delay * 2, 300)
    raise RuntimeError('max retries exceeded')


# ---------------------------------------------------------------- main loop
def run_eval_main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--provider', choices=['gemini', 'openai'], default='gemini')
    ap.add_argument('--model', required=True)
    ap.add_argument('--base-url', default='https://api.openai.com/v1')
    ap.add_argument('--api-key-env', default='OPENAI_API_KEY')
    ap.add_argument('--items', default=os.path.join(ROOT, 'data/subset_items.jsonl'))
    ap.add_argument('--ur-options', default=os.path.join(ROOT, 'data/options_ur.jsonl'),
                    help='jsonl {uid, options_ur}; required for the Urdu script (not in the public U-MIRAGE release)')
    ap.add_argument('--ur-original-questions', action='store_true', help='use the released (truncated) Urdu questions')
    ap.add_argument('--scripts', nargs='+', default=['en', 'ru', 'ur'])
    ap.add_argument('--conds', nargs='+', default=['zs', 'cot'])
    ap.add_argument('--temperature', type=float, default=0.1)
    ap.add_argument('--max-tokens', type=int, default=4096)
    ap.add_argument('--thinking-level', default=None, help='Gemini 3+/4: minimal|low|medium|high')
    ap.add_argument('--thinking-budget', type=int, default=None, help='Gemini 2.5: 0 disables thinking on Flash')
    ap.add_argument('--no-temperature', action='store_true', help='OpenAI reasoning models that only allow default temperature')
    ap.add_argument('--max-tokens-param', default='max_completion_tokens', help='OpenAI: max_completion_tokens (new) or max_tokens (legacy servers)')
    ap.add_argument('--reasoning-effort', default=None, help='OpenAI-compatible reasoning models')
    ap.add_argument('--rpm', type=float, default=5, help='client-side throttle (requests per minute)')
    ap.add_argument('--max-calls', type=int, default=None, help='stop after this many successful calls (quota budgeting)')
    ap.add_argument('--limit', type=int, default=None, help='only the first N subset items (smoke test)')
    ap.add_argument('--interleave', action='store_true', help='round-robin across script/cond so partial runs stay balanced')
    ap.add_argument('--workers', type=int, default=1, help='concurrent requests (RPM throttle still applies)')
    ap.add_argument('--ids', default=None, help='csv with a uid column: restrict to these items (e.g. data/sample366_ids.csv)')
    ap.add_argument('--order', choices=['file', 'shuffle'], default='shuffle')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--spend-this-model-only', action='store_true', help='count only this model\'s results toward the cost cap')
    ap.add_argument('--max-cost-usd', type=float, default=None, help='stop when estimated spend (all logs since --spend-since) exceeds this')
    ap.add_argument('--spend-since', default='2026-11-22T08:00', help='UTC ISO prefix; calls before this are treated as free tier')
    ap.add_argument('--price-in', type=float, default=0.30, help='USD per 1M input tokens')
    ap.add_argument('--price-out', type=float, default=2.50, help='USD per 1M output+thinking tokens')
    ap.add_argument('--timeout', type=int, default=180)
    ap.add_argument('--max-retries', type=int, default=8)
    ap.add_argument('--outdir', default=os.path.join(ROOT, 'results'))
    args = ap.parse_args(argv)

    items = [json.loads(l) for l in open(args.items)]
    if args.ids:
        import csv
        keep = {r['uid'] for r in csv.DictReader(open(args.ids))}
        items = [it for it in items if it['uid'] in keep]
    if args.limit:
        items = items[:args.limit]
    if args.order == 'shuffle':  # fixed-seed random order so partial runs are not biased by source
        import numpy as np
        perm = np.random.RandomState(args.seed).permutation(len(items))
        items = [items[i] for i in perm]
    if os.path.exists(args.ur_options):
        uo = {j['uid']: j['options_ur'] for j in map(json.loads, open(args.ur_options))}
        for it in items:
            if it['uid'] in uo:
                it['options_ur'] = uo[it['uid']]
        qf = os.path.join(ROOT, 'data/questions_ur_fixed.jsonl')
        if os.path.exists(qf) and not args.ur_original_questions:
            fx = {j['uid']: j['question_ur_fixed'] for j in map(json.loads, open(qf))}
            for it in items:
                if it['uid'] in fx:
                    it['question_ur'] = fx[it['uid']]; it['ur_question_fixed'] = True
            missing = [it['uid'] for it in items if it.get('ur_truncated', it.get('ur_maybe_truncated')) and not it.get('ur_question_fixed')]
            if missing and 'ur' in args.scripts:
                print(f'!! {len(missing)} truncated Urdu questions not yet fixed; skipping them for ur')
                for it in items:
                    if it['uid'] in missing: it.pop('options_ur', None)
    elif 'ur' in args.scripts:
        print(f'!! {args.ur_options} not found: Urdu-script options are not in the public U-MIRAGE release; skipping ur.')
        args.scripts = [s for s in args.scripts if s != 'ur']

    mdir = os.path.join(args.outdir, args.model.replace('/', '_'))
    os.makedirs(mdir, exist_ok=True)
    jobs = {}
    for s in args.scripts:
        for c in args.conds:
            path = os.path.join(mdir, f'{s}_{c}.jsonl')
            done = set()
            if os.path.exists(path):
                done = {json.loads(l)['uid'] for l in open(path) if l.strip()}
            jobs[(s, c)] = (path, [it for it in items if it['uid'] not in done and it.get(f'options_{s}')])
            print(f'{s}/{c}: {len(done)} done, {len(jobs[(s, c)][1])} to go')
    order = []
    if args.interleave:
        queues = {k: list(v[1]) for k, v in jobs.items()}
        while any(queues.values()):
            for k in list(queues):
                if queues[k]:
                    order.append((k, queues[k].pop(0)))
    else:
        order = [(k, it) for k, v in jobs.items() for it in v[1]]

    def cost_of(u):
        u = u or {}
        if 'prompt_tokens' in u:  # OpenAI: completion_tokens already include reasoning tokens
            return (u.get('prompt_tokens', 0) * args.price_in + u.get('completion_tokens', 0) * args.price_out) / 1e6
        return (u.get('promptTokenCount', 0) * args.price_in + (u.get('candidatesTokenCount', 0) + u.get('thoughtsTokenCount', 0)) * args.price_out) / 1e6
    spent = 0.0
    if args.max_cost_usd is not None:
        if args.spend_this_model_only:
            logs = glob.glob(os.path.join(mdir, '*.jsonl'))
        else:
            logs = glob.glob(os.path.join(args.outdir, '*', '*.jsonl')) + [os.path.join(ROOT, 'data/urdu_fix_log.jsonl')]
        for lf in logs:
            if os.path.exists(lf):
                for l in open(lf):
                    try: r = json.loads(l)
                    except Exception: continue
                    if r.get('t_start', '') >= args.spend_since:
                        spent += cost_of(r.get('usage'))
        print(f'estimated spend so far since {args.spend_since}Z: ${spent:.3f} (cap ${args.max_cost_usd})', flush=True)
    import threading
    from concurrent.futures import ThreadPoolExecutor
    gap = 60.0 / args.rpm
    lock, wlock, stop = threading.Lock(), threading.Lock(), threading.Event()
    state = {'next': 0.0, 'ok': 0, 'issued': 0, 'spent': spent}

    def work(job):
        (s, c), it = job
        if stop.is_set():
            return
        if args.max_cost_usd is not None and state['spent'] >= args.max_cost_usd:
            if not stop.is_set(): print(f'!! cost cap reached (${state["spent"]:.3f}), stopping', flush=True)
            stop.set(); return
        with lock:  # shared client-side RPM throttle + call budget
            if args.max_calls is not None and state['issued'] >= args.max_calls:
                stop.set(); return
            state['issued'] += 1
            slot = max(time.time(), state['next']); state['next'] = slot + gap
        if slot > time.time():
            time.sleep(slot - time.time())
        if stop.is_set():
            return
        prompt = build_prompt(it, s, c)
        t0 = dt.datetime.now(dt.timezone.utc)
        try:
            out, retries = call_with_retry(args, prompt)
        except QuotaExhausted as e:
            if not stop.is_set():
                print('!! daily quota exhausted, stopping (rerun later to resume):', str(e)[:300], flush=True)
            stop.set(); return
        except (RuntimeError, SystemExit) as e:
            print(f'!! {s}/{c} {it["uid"]} failed: {e}', flush=True); return
        pred, how = parse_answer(out['text'], it['options_en'].keys(), c)
        rec = dict(uid=it['uid'], source=it['source'], script=s, cond=c, gold=it['answer'], pred=pred,
                   correct=pred == it['answer'], parse=how, ur_question_fixed=it.get('ur_question_fixed', False) if s == 'ur' else None, response=out['text'], finish_reason=out['finish_reason'],
                   model=args.model, model_version=out['model_version'], response_id=out['response_id'],
                   usage=out['usage'], temperature=args.temperature, thinking_level=args.thinking_level,
                   thinking_budget=args.thinking_budget, retries=retries, prompt=prompt,
                   provider=args.provider, reasoning_effort=args.reasoning_effort,
                   temperature_sent=None if (args.provider == 'openai' and args.no_temperature) else args.temperature,
                   max_tokens=args.max_tokens, errors=out.get('errors'), system_fingerprint=out.get('system_fingerprint'),
                   service_tier=out.get('service_tier'), refusal=out.get('refusal'),
                   ur_question_truncated_in_original=it.get('ur_question_truncated_in_original', it.get('ur_truncated')) if s == 'ur' else None,
                   latency_s=round((dt.datetime.now(dt.timezone.utc) - t0).total_seconds(), 3),
                   t_start=t0.isoformat(), t_end=dt.datetime.now(dt.timezone.utc).isoformat())
        with wlock:
            with open(jobs[(s, c)][0], 'a') as f:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            state['ok'] += 1
            state['spent'] += cost_of(out['usage'])
            u = out['usage'] or {}
            print(f'{state["ok"]} {s}/{c} {it["uid"]} gold={it["answer"]} pred={pred} ({how}) '
                  f'tok={u.get("totalTokenCount", u.get("total_tokens"))}', flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, order))
    n_ok = state['ok']
    print('done; successful calls this session:', n_ok, f'| est. spend since {args.spend_since}Z: ${state["spent"]:.3f}')


if __name__ == '__main__':
    run_eval_main()
