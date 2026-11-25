#!/usr/bin/env python3
"""Urdu-script fix, v2 (one item per call, strict-script prompt, max 2 attempts per item).
Attempt 1: temperature 0; attempt 2 (only if attempt 1 fails validation): temperature 0.5.
Items still failing are written to data/urdu_handfix_needed.csv for a human Urdu speaker.
Acceptance (questions): no foreign-script characters, >=60% Arabic-script letters, and either ends with sentence
punctuation and len >= 0.6*len(EN), or len >= 0.85*len(EN) (MedMCQA/MMLU stems often have no final punctuation).
Acceptance (options): same letters as EN, all non-empty, >=50% Arabic-script letters, no foreign-script characters.
  python scripts/fix_urdu_v2.py --ids data/sample366_ids.csv --rpm 14
"""
import argparse, csv, json, os, re, sys, time, datetime as dt
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_urdu import ROOT, D, YN, END, OPT_PROMPT, Q_PROMPT, SCRIPT_RULE, bad_chars, ur_share, parse_json

STATS = {'ok': 0, '429': 0, '503': 0, '402': 0, 'other_err': 0}


class DailyCap(Exception):
    pass


def call(model, prompt, temperature):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    body = {'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
            'generationConfig': {'temperature': temperature, 'maxOutputTokens': 16384, 'responseMimeType': 'application/json',
                                 'thinkingConfig': {'thinkingLevel': 'minimal'}}}
    delay = 10
    for attempt in range(8):
        t0 = dt.datetime.now(dt.timezone.utc)
        try:
            r = requests.post(url, json=body, timeout=180, headers={'x-goog-api-key': os.environ['GEMINI_API_KEY']})
            code, d = r.status_code, r.json()
        except Exception as e:
            code, d = -1, {'exc': str(e)}
        if code == 200:
            STATS['ok'] += 1
            cand = d['candidates'][0]
            text = ''.join(p.get('text', '') for p in cand.get('content', {}).get('parts', []) if not p.get('thought'))
            with open(D('urdu_fix_log.jsonl'), 'a') as f:
                f.write(json.dumps(dict(t_start=t0.isoformat(), t_end=dt.datetime.now(dt.timezone.utc).isoformat(), model=model,
                                        model_version=d.get('modelVersion'), usage=d.get('usageMetadata'), finish_reason=cand.get('finishReason'),
                                        prompt=prompt, response=text, fixer='v2', temperature=temperature), ensure_ascii=False) + '\n')
            return text
        key = str(code) if str(code) in STATS else 'other_err'
        STATS[key] += 1
        if code == 402:
            raise DailyCap('HTTP 402 billing: ' + json.dumps(d)[:300])
        if code == 429:
            viol = [v for det in d.get('error', {}).get('details', []) for v in det.get('violations', [])]
            if any('PerDay' in v.get('quotaId', '') for v in viol):
                with open(os.path.join(ROOT, 'quota_errors.log'), 'a') as qf:
                    qf.write(dt.datetime.now(dt.timezone.utc).isoformat() + ' fix_urdu_v2 ' + json.dumps(d) + '\n')
                raise DailyCap('daily cap: ' + ', '.join(f"{v.get('quotaId')}={v.get('quotaValue')}" for v in viol))
            wait = 60
            for det in d['error'].get('details', []):
                if det.get('@type', '').endswith('RetryInfo'):
                    wait = float(det['retryDelay'].rstrip('s')) + 2
        else:
            wait = delay; delay = min(delay * 2, 180)
        print(f'  [{code}] wait {wait:.0f}s', flush=True)
        time.sleep(wait)
    raise RuntimeError('API retries exhausted')


def check_q(q, it):
    if not isinstance(q, str) or not q.strip():
        return 'empty/invalid output'
    q = q.strip(); b = bad_chars(q)
    if b: return 'foreign-script characters: ' + ''.join(dict.fromkeys(b))
    if ur_share(q) < 0.6: return f'only {ur_share(q):.0%} Urdu-script letters'
    E = len(it['question_en'])
    if not ((q.endswith(END) and len(q) >= 0.6 * E) or len(q) >= 0.85 * E):
        return f'looks incomplete (len {len(q)} vs EN {E}, ends {q[-3:]!r})'
    return None


def check_o(o, it):
    if not isinstance(o, dict) or sorted(o) != sorted(it['options_en']):
        return 'wrong/missing option letters'
    if not all(isinstance(v, str) and v.strip() for v in o.values()): return 'empty option'
    j = ' '.join(o.values()); b = bad_chars(j)
    if b: return 'foreign-script characters: ' + ''.join(dict.fromkeys(b))
    latin_only = all(re.fullmatch(r"[A-Z0-9\s.\-–%/+,:;()<>=≥≤×°µ]+", v.strip()) for v in it['options_en'].values())
    if not latin_only and ur_share(j) < 0.5:  # numbers / abbreviations (e.g. '2-3%', 'CABG') legitimately stay in Latin
        return f'only {ur_share(j):.0%} Urdu-script letters'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='gemini-3.5-flash-lite')
    ap.add_argument('--ids', required=True)
    ap.add_argument('--rpm', type=float, default=14)
    ap.add_argument('--max-calls', type=int, default=150)
    args = ap.parse_args()
    keep = {r['uid'] for r in csv.DictReader(open(args.ids))}
    items = [json.loads(l) for l in open(D('subset_items.jsonl'))]
    items = [it for it in items if it['uid'] in keep]
    done_o = {j['uid'] for j in map(json.loads, open(D('options_ur.jsonl')))}
    done_q = {j['uid'] for j in map(json.loads, open(D('questions_ur_fixed.jsonl')))}
    hf_path = D('urdu_handfix_needed.csv')
    prev_hf = {(r['uid'], r['field']) for r in csv.DictReader(open(hf_path))} if os.path.exists(hf_path) else set()
    jobs = [('options', it) for it in items if it['uid'] not in done_o] + \
           [('question', it) for it in items if it.get('ur_truncated') and it['uid'] not in done_q]
    jobs = [j for j in jobs if (j[1]['uid'], j[0]) not in prev_hf]
    print(f'jobs: {sum(j[0]=="options" for j in jobs)} option sets, {sum(j[0]=="question" for j in jobs)} questions', flush=True)
    last, n_calls, fixed, failed = 0.0, 0, {'options': 0, 'question': 0}, []
    try:
        for field, it in jobs:
            best, reason = None, None
            for attempt, temp in enumerate([0.0, 0.5], 1):
                if n_calls >= args.max_calls:
                    raise DailyCap('max-calls reached (local budget)')
                w = last + 60 / args.rpm - time.time()
                if w > 0: time.sleep(w)
                last = time.time(); n_calls += 1
                if field == 'options':
                    payload = json.dumps({it['uid']: {'roman_urdu': it['options_ru'], 'english_reference': it['options_en']}}, ensure_ascii=False, indent=1)
                    pr = SCRIPT_RULE + '\n' + OPT_PROMPT.format(payload=payload)
                else:
                    pr = SCRIPT_RULE + '\n' + Q_PROMPT.format(payload=json.dumps({it['uid']: it['question_en']}, ensure_ascii=False, indent=1))
                try:
                    out = parse_json(call(args.model, pr, temp)).get(it['uid'])
                except (json.JSONDecodeError, AttributeError) as e:
                    out, reason = None, f'unparseable JSON ({e})'
                except RuntimeError as e:
                    out, reason = None, str(e)
                if out is not None:
                    reason = check_o(out, it) if field == 'options' else check_q(out, it)
                    best = out
                if out is not None and reason is None:
                    meth = f'{args.model} v2 strict-script prompt, 1 item/call, attempt {attempt}, temp {temp}'
                    if field == 'options':
                        rec = dict(uid=it['uid'], options_ur=out, method=meth.replace('v2', 'RU->Urdu script (EN as reference), v2'))
                        with open(D('options_ur.jsonl'), 'a') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')
                    else:
                        rec = dict(uid=it['uid'], question_ur_original=it['question_ur'], question_ur_fixed=out.strip(),
                                   method=meth.replace('v2', 'EN->Urdu full retranslation, maxOutputTokens 16384, v2'))
                        with open(D('questions_ur_fixed.jsonl'), 'a') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')
                    fixed[field] += 1
                    print(f'OK  {field} {it["uid"]} (attempt {attempt})', flush=True)
                    break
                print(f'BAD {field} {it["uid"]} attempt {attempt}: {reason}', flush=True)
            else:
                if best is None and reason and 'API retries exhausted' in reason:
                    print(f'SKIP {field} {it["uid"]}: API unavailable (503/429), left pending for a later run', flush=True)
                    continue
                failed.append(dict(uid=it['uid'], source=it['source'], field=field,
                                   english=json.dumps(it['options_en'], ensure_ascii=False) if field == 'options' else it['question_en'],
                                   roman_urdu=json.dumps(it['options_ru'], ensure_ascii=False) if field == 'options' else it['question_ru'],
                                   best_attempt=json.dumps(best, ensure_ascii=False) if isinstance(best, dict) else (best or ''),
                                   reason=reason))
    except DailyCap as e:
        print('!! STOP:', e, '|', dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S PKT'), flush=True)
    finally:
        if failed:
            new = not os.path.exists(hf_path)
            with open(hf_path, 'a', newline='') as f:
                w = csv.DictWriter(f, fieldnames=['uid', 'source', 'field', 'english', 'roman_urdu', 'best_attempt', 'reason'])
                if new: w.writeheader()
                w.writerows(failed)
        print(f'calls {n_calls} | fixed {fixed} | failed {len(failed)} | http {STATS}', flush=True)


if __name__ == '__main__':
    main()
