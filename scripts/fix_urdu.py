#!/usr/bin/env python3
"""Repair the Urdu-script side of the subset (public U-MIRAGE release lacks it):
 (1) data/options_ur.jsonl: Urdu-script option texts for every subset item
     - yes/no(/maybe) items (PubMedQA, BioASQ): fixed dictionary  yes->ہاں, no->نہیں, maybe->شاید
     - all others: Roman Urdu options (the released U-MIRAGE options) transliterated/translated into Urdu script by
       the model, with the English options shown only as a meaning reference; batched 10 items per call, JSON out.
 (2) data/questions_ur_fixed.jsonl: the subset questions flagged ur_maybe_truncated are retranslated from the
     English original into Urdu script (no output cap: maxOutputTokens 16384), 5 per call. Original kept alongside.
Every call is logged to data/urdu_fix_log.jsonl (prompt, raw response, model version, usage, time).
Resumable; validates Urdu-script share, completeness, option keys; failed batches are retried item by item.
"""
import argparse, json, os, re, time, datetime as dt
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda p: os.path.join(ROOT, 'data', p)
YN = {'yes': 'ہاں', 'no': 'نہیں', 'maybe': 'شاید'}
END = ('۔', '?', '؟', '.', '!', ':')

OPT_PROMPT = """You are a professional medical translator. Convert the following Roman Urdu multiple-choice options into proper Urdu script (Nastaliq/Arabic script), preserving medical terminology. Medical terms that are kept in English in the Roman Urdu should be written in Urdu script the way Urdu medical texts normally write them (transliterated), not left in Latin letters; keep numbers, units, and standard abbreviations (e.g. DNA, mmHg, IgG) as they are. The English original of each option is given only so you understand the meaning; translate the Roman Urdu wording.
Return ONLY a JSON object mapping each item id to an object of option letter -> Urdu-script text, with exactly the same ids and letters as the input.

INPUT:
{payload}"""

Q_PROMPT = """You are a professional medical translator. Translate each of the following English medical exam questions completely into Urdu (Urdu script), preserving medical terminology. Translate the whole question to the end, including every sentence and the final question; do not summarize or shorten. Medical terms without a common Urdu equivalent may be transliterated into Urdu script; keep numbers, units, lab values and standard abbreviations as they are.
Return ONLY a JSON object mapping each item id to its full Urdu translation.

INPUT:
{payload}"""


PASHTO_ETC = set('ټډړښږګڼځڅۍېۀ')
def bad_chars(s):
    out = []
    for ch in s:
        o = ord(ch)
        ok = o < 0x250 or 0x370 <= o <= 0x3FF or 0x600 <= o <= 0x6FF or 0x750 <= o <= 0x77F or 0xFB50 <= o <= 0xFEFF \
             or 0x2000 <= o <= 0x22FF or o in (0x200C, 0x200D)
        if not ok or ch in PASHTO_ETC:
            out.append(ch)
    return out


SCRIPT_RULE = """STRICT SCRIPT RULE: write ONLY in Urdu script (Arabic-script letters used in Urdu: ا ب پ ت ٹ ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن ں و ہ ھ ء ی ے, plus Urdu diacritics and punctuation ، ۔ ؟).
NEVER output Bengali letters (e.g. ক জ ড ে ি), Devanagari letters (e.g. क ह ि), Japanese/Chinese characters, Ethiopic letters, or Pashto-only letters (ټ ډ ړ ښ ګ ڼ ې). Before answering, check every word: if any letter is not an Urdu letter, rewrite that word in Urdu letters.
English medical terms must be transliterated with Urdu letters only. Examples:
- "Glycogen phosphorylase" -> "گلائکوجن فاسفوریلیز"
- "10 mL/kg 10% dextrose" -> "10 mL/kg 10% ڈیکسٹروز"
- "Hemochromatosis" -> "ہیموکرومیٹوسس"
- "isoleucine" -> "آئسولیوسین"
- "ultrasound" -> "الٹراساؤنڈ"
- "A 45-year-old man presents with chest pain." -> "ایک 45 سالہ مرد سینے میں درد کے ساتھ آتا ہے۔"
Numbers, units, lab values and standard abbreviations (DNA, mmHg, IgG, CT, HbA1c) stay as they are in Latin letters/digits.
"""


def ur_share(s):
    ar = len(re.findall(r'[\u0600-\u06FF]', s)); la = len(re.findall(r'[A-Za-z]', s))
    return ar / max(ar + la, 1)


def call(args, prompt):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{args.model}:generateContent'
    body = {'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
            'generationConfig': {'temperature': args.temperature, 'maxOutputTokens': 16384, 'responseMimeType': 'application/json',
                                 'thinkingConfig': {'thinkingLevel': args.thinking_level}}}
    delay = 10
    for attempt in range(8):
        t0 = dt.datetime.now(dt.timezone.utc)
        try:
            r = requests.post(url, json=body, timeout=300, headers={'x-goog-api-key': os.environ['GEMINI_API_KEY']})
            d = r.json()
        except Exception as e:
            d, r = {'exc': str(e)}, None
        if r is not None and r.status_code == 200:
            cand = d['candidates'][0]
            text = ''.join(p.get('text', '') for p in cand.get('content', {}).get('parts', []) if not p.get('thought'))
            with open(D('urdu_fix_log.jsonl'), 'a') as f:
                f.write(json.dumps(dict(t_start=t0.isoformat(), t_end=dt.datetime.now(dt.timezone.utc).isoformat(),
                                        model=args.model, model_version=d.get('modelVersion'), usage=d.get('usageMetadata'),
                                        finish_reason=cand.get('finishReason'), prompt=prompt, response=text), ensure_ascii=False) + '\n')
            return text
        if r is not None and r.status_code == 402:
            with open(os.path.join(ROOT, 'quota_errors.log'), 'a') as qf:
                qf.write(dt.datetime.now(dt.timezone.utc).isoformat() + ' fix_urdu ' + json.dumps(d) + '\n')
            raise SystemExit('HTTP 402 billing/prepayment stop')
        if r is not None and r.status_code == 429:
            if any('PerDay' in v.get('quotaId', '') for det in d['error'].get('details', []) for v in det.get('violations', [])):
                with open(os.path.join(ROOT, 'quota_errors.log'), 'a') as qf:
                    qf.write(dt.datetime.now(dt.timezone.utc).isoformat() + ' fix_urdu ' + json.dumps(d) + '\n')
                raise SystemExit('daily quota exhausted; rerun later to resume')
        print(f'  retry {attempt+1}: {json.dumps(d)[:160]}', flush=True)
        time.sleep(delay); delay = min(delay * 2, 300)
    raise RuntimeError('max retries')


def parse_json(text):
    text = text.strip()
    text = re.sub(r'^```(?:json)?|```$', '', text).strip()
    return json.loads(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='gemini-3.5-flash-lite')
    ap.add_argument('--thinking-level', default='minimal')
    ap.add_argument('--rpm', type=float, default=3)
    ap.add_argument('--max-calls', type=int, default=200)
    ap.add_argument('--opt-batch', type=int, default=10)
    ap.add_argument('--q-batch', type=int, default=5)
    ap.add_argument('--ids', default=None, help='csv with a uid column to restrict to')
    ap.add_argument('--prompt-version', type=int, default=1, help='2 = strict-script rule + transliteration examples')
    ap.add_argument('--only', choices=['both', 'options', 'questions'], default='both')
    ap.add_argument('--max-items', type=int, default=None, help='only attempt this many pending items per stage (pilot)')
    ap.add_argument('--retry-items', action='store_true', help='retry failed items one by one right away')
    ap.add_argument('--temperature', type=float, default=0.0)
    args = ap.parse_args()
    items = [json.loads(l) for l in open(D('subset_items.jsonl'))]
    if args.ids:
        import csv
        keep = {r['uid'] for r in csv.DictReader(open(args.ids))}
        items = [it for it in items if it['uid'] in keep]
    done_o = {j['uid'] for j in map(json.loads, open(D('options_ur.jsonl')))} if os.path.exists(D('options_ur.jsonl')) else set()
    done_q = {j['uid'] for j in map(json.loads, open(D('questions_ur_fixed.jsonl')))} if os.path.exists(D('questions_ur_fixed.jsonl')) else set()
    calls, last = [0], [0.0]
    global FAILS
    FAILS = []

    def throttled(prompt):
        if calls[0] >= args.max_calls:
            raise SystemExit('max-calls reached')
        w = last[0] + 60 / args.rpm - time.time()
        if w > 0: time.sleep(w)
        last[0] = time.time(); calls[0] += 1
        return call(args, prompt)

    # (1a) yes/no items: dictionary
    with open(D('options_ur.jsonl'), 'a') as f:
        for it in items:
            if it['uid'] in done_o: continue
            en = {k: v.strip().lower().rstrip('.') for k, v in it['options_en'].items()}
            if all(v in YN for v in en.values()):
                f.write(json.dumps(dict(uid=it['uid'], options_ur={k: YN[v] for k, v in en.items()},
                                        method='dictionary yes/no/maybe'), ensure_ascii=False) + '\n')
                done_o.add(it['uid'])
    # (1b) model-converted options
    todo = [it for it in items if it['uid'] not in done_o] if args.only in ('both', 'options') else []
    todo = todo[:args.max_items] if args.max_items else todo
    def do_opts(batch):
        payload = json.dumps({it['uid']: {'roman_urdu': it['options_ru'], 'english_reference': it['options_en']} for it in batch},
                             ensure_ascii=False, indent=1)
        pr = OPT_PROMPT.format(payload=payload)
        if args.prompt_version == 2: pr = SCRIPT_RULE + '\n' + pr
        out = parse_json(throttled(pr))
        good = []
        for it in batch:
            o = out.get(it['uid'])
            if isinstance(o, dict) and sorted(o) == sorted(it['options_en']) and all(isinstance(v, str) and v.strip() for v in o.values()) \
                    and ur_share(' '.join(o.values())) >= 0.5 and not bad_chars(' '.join(o.values())):
                good.append(dict(uid=it['uid'], options_ur=o, method=f'{args.model} RU->Urdu script (EN as reference), batch {len(batch)}, temp {args.temperature}, prompt v{args.prompt_version}'))
        return good
    while todo:
        batch, todo = todo[:args.opt_batch], todo[args.opt_batch:]
        try:
            good = do_opts(batch)
        except (json.JSONDecodeError, KeyError, RuntimeError) as e:
            print('batch failed:', e); good = []
        miss = [it for it in batch if it['uid'] not in {g['uid'] for g in good}]
        for it in (miss if len(batch) > 1 and args.retry_items else []):
            try: good += do_opts([it])
            except (json.JSONDecodeError, KeyError, RuntimeError) as e: print('item failed', it['uid'], e)
        for it in batch:
            if it['uid'] not in {g['uid'] for g in good}: FAILS.append(('options', it['uid']))
        with open(D('options_ur.jsonl'), 'a') as f:
            for g in good: f.write(json.dumps(g, ensure_ascii=False) + '\n')
        print(f'options: +{len(good)} (calls {calls[0]})', flush=True)
    # (2) truncated questions
    todo = [it for it in items if it.get('ur_truncated', it['ur_maybe_truncated']) and it['uid'] not in done_q] if args.only in ('both', 'questions') else []
    todo = todo[:args.max_items] if args.max_items else todo
    def do_q(batch):
        payload = json.dumps({it['uid']: it['question_en'] for it in batch}, ensure_ascii=False, indent=1)
        pr = Q_PROMPT.format(payload=payload)
        if args.prompt_version == 2: pr = SCRIPT_RULE + '\n' + pr
        out = parse_json(throttled(pr))
        good = []
        for it in batch:
            q = out.get(it['uid'])
            if isinstance(q, str) and not bad_chars(q) and ur_share(q) >= 0.6 and q.strip().endswith(END) and len(q) > 0.6 * len(it['question_en']):
                good.append(dict(uid=it['uid'], question_ur_original=it['question_ur'], question_ur_fixed=q.strip(),
                                 method=f'{args.model} EN->Urdu full retranslation, batch {len(batch)}, temp {args.temperature}, maxOutputTokens 16384, prompt v{args.prompt_version}'))
        return good
    while todo:
        batch, todo = todo[:args.q_batch], todo[args.q_batch:]
        try: good = do_q(batch)
        except (json.JSONDecodeError, KeyError, RuntimeError) as e: print('batch failed:', e); good = []
        miss = [it for it in batch if it['uid'] not in {g['uid'] for g in good}]
        for it in (miss if len(batch) > 1 and args.retry_items else []):
            try: good += do_q([it])
            except (json.JSONDecodeError, KeyError, RuntimeError) as e: print('item failed', it['uid'], e)
        for it in batch:
            if it['uid'] not in {g['uid'] for g in good}: FAILS.append(('question', it['uid']))
        with open(D('questions_ur_fixed.jsonl'), 'a') as f:
            for g in good: f.write(json.dumps(g, ensure_ascii=False) + '\n')
        print(f'questions: +{len(good)} (calls {calls[0]})', flush=True)
    print('fix_urdu done; calls', calls[0], '| failed this run:', len(FAILS), FAILS)


if __name__ == '__main__':
    main()
