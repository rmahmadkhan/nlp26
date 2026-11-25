#!/usr/bin/env python3
"""Local (GPU or CPU) Hugging Face transformers runner for the NLP project U-MIRAGE replication.

Same prompts (imported from run_eval.build_prompt), same parser, same item order (fixed-seed shuffle,
interleaved across script/cond), same output record schema as run_eval.py, so scripts/score.py works
unchanged on results/<tag>/<script>_<cond>.jsonl. Resumable: skips uids already in each file, appends.

  python scripts/run_local_hf.py --model-id Qwen/Qwen3.5-0.8B --tag qwen3.5-0.8b-bnb4 --quant bnb4 \
      --items share/nlp_project_sample366.jsonl --ur-original-questions --conds zs umcot
"""
import argparse, json, os, sys, time, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_eval import build_prompt, parse_answer, PARSER_VERSION  # identical prompts + parser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_items(args):
    items = [json.loads(l) for l in open(args.items)]
    if args.ids:
        import csv
        keep = {r['uid'] for r in csv.DictReader(open(args.ids))}
        items = [it for it in items if it['uid'] in keep]
    if args.limit:
        items = items[:args.limit]
    if args.order == 'shuffle':  # same as run_eval.py
        perm = np.random.RandomState(args.seed).permutation(len(items))
        items = [items[i] for i in perm]
    # Urdu options: the shared sample already carries options_ur; otherwise merge them like run_eval.py
    if any('options_ur' not in it for it in items) and os.path.exists(args.ur_options):
        uo = {j['uid']: j['options_ur'] for j in map(json.loads, open(args.ur_options))}
        for it in items:
            if it['uid'] in uo and 'options_ur' not in it:
                it['options_ur'] = uo[it['uid']]
    if not args.ur_original_questions:
        qf = os.path.join(ROOT, 'data/questions_ur_fixed.jsonl')
        if os.path.exists(qf):
            fx = {j['uid']: j['question_ur_fixed'] for j in map(json.loads, open(qf))}
            for it in items:
                if it['uid'] in fx:
                    it['question_ur'] = fx[it['uid']]; it['ur_question_fixed'] = True
    return items


def load_model(args):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    dtype = {'bf16': torch.bfloat16, 'fp16': torch.float16, 'fp32': torch.float32}[args.dtype]
    kw = dict(dtype=dtype, token=os.environ.get('HF_TOKEN') or None)
    if args.quant == 'bnb4':
        from transformers import BitsAndBytesConfig
        kw['quantization_config'] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                                                       bnb_4bit_compute_dtype=dtype, bnb_4bit_use_double_quant=False)
        kw['device_map'] = 'auto'
    elif torch.cuda.is_available():
        kw['device_map'] = 'cuda'
    tok = AutoTokenizer.from_pretrained(args.model_id, token=kw['token'])
    tok.padding_side = 'left'
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    try:
        model = AutoModelForCausalLM.from_pretrained(args.model_id, **kw)
    except (ValueError, KeyError) as e:  # multimodal checkpoints -> image-text-to-text class
        print('AutoModelForCausalLM failed, trying AutoModelForImageTextToText:', str(e)[:200])
        from transformers import AutoModelForImageTextToText
        model = AutoModelForImageTextToText.from_pretrained(args.model_id, **kw)
    model.eval()
    return tok, model


def chat_text(tok, prompt):
    msgs = [{'role': 'user', 'content': prompt}]
    try:  # Qwen3/3.5: hard-disable thinking; other templates ignore the extra kwarg
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def run_local_hf_main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--model-id', required=True, help='Hugging Face repo id')
    ap.add_argument('--tag', required=True, help='results/<tag>/ folder name, e.g. llama3.2-1b-instruct-bf16')
    ap.add_argument('--quant', choices=['none', 'bnb4'], default='none', help='bnb4 = bitsandbytes 4-bit NF4 (the paper\'s "q" rows)')
    ap.add_argument('--dtype', choices=['bf16', 'fp16', 'fp32'], default='bf16')
    ap.add_argument('--items', default=os.path.join(ROOT, 'share/nlp_project_sample366.jsonl'))
    ap.add_argument('--ur-options', default=os.path.join(ROOT, 'data/options_ur.jsonl'))
    ap.add_argument('--ur-original-questions', action='store_true')
    ap.add_argument('--ids', default=None)
    ap.add_argument('--scripts', nargs='+', default=['en', 'ru', 'ur'])
    ap.add_argument('--conds', nargs='+', default=['zs', 'umcot'])
    ap.add_argument('--temperature', type=float, default=0.1)
    ap.add_argument('--max-tokens', type=int, default=2048)
    ap.add_argument('--batch-size', type=int, default=16)
    ap.add_argument('--order', choices=['file', 'shuffle'], default='shuffle')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--max-calls', type=int, default=None)
    ap.add_argument('--outdir', default=os.path.join(ROOT, 'results'))
    args = ap.parse_args(argv)

    import torch
    items = load_items(args)
    mdir = os.path.join(args.outdir, args.tag)
    os.makedirs(mdir, exist_ok=True)
    jobs = {}
    for s in args.scripts:
        for c in args.conds:
            path = os.path.join(mdir, f'{s}_{c}.jsonl')
            done = {json.loads(l)['uid'] for l in open(path) if l.strip()} if os.path.exists(path) else set()
            jobs[(s, c)] = (path, [it for it in items if it['uid'] not in done and it.get(f'options_{s}')])
            print(f'{s}/{c}: {len(done)} done, {len(jobs[(s, c)][1])} to go', flush=True)
    queues = {k: list(v[1]) for k, v in jobs.items()}
    order = []
    while any(queues.values()):  # interleave (same as run_eval --interleave)
        for k in list(queues):
            if queues[k]:
                order.append((k, queues[k].pop(0)))
    if args.max_calls:
        order = order[:args.max_calls]
    if not order:
        print('nothing to do'); return

    import transformers
    tok, model = load_model(args)
    dev = next(model.parameters()).device
    rev = getattr(model.config, '_commit_hash', None)
    if not rev:
        try:
            from huggingface_hub import HfApi
            rev = HfApi().model_info(args.model_id, token=os.environ.get('HF_TOKEN') or None).sha
        except Exception as e:
            rev = f'unknown ({type(e).__name__})'
    gen_kw = dict(max_new_tokens=args.max_tokens, pad_token_id=tok.pad_token_id)
    if args.temperature > 0:  # override checkpoint generation_config defaults (top_k/top_p/penalties) for parity
        gen_kw.update(do_sample=True, temperature=args.temperature, top_p=1.0, top_k=0, repetition_penalty=1.0)
    else:
        gen_kw.update(do_sample=False)
    eos = {int(x) for x in np.atleast_1d(getattr(model.generation_config, 'eos_token_id', None) or [])} | {tok.eos_token_id}
    hw = torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'
    print(f'model {args.model_id} rev={rev} quant={args.quant} dtype={args.dtype} device={dev} ({hw}) | {len(order)} calls', flush=True)
    n_ok, t_all = 0, time.time()
    for b0 in range(0, len(order), args.batch_size):
        batch = order[b0:b0 + args.batch_size]
        prompts = [build_prompt(it, s, c) for (s, c), it in batch]
        texts = [chat_text(tok, p) for p in prompts]
        enc = tok(texts, return_tensors='pt', padding=True, add_special_tokens=False).to(dev)
        torch.manual_seed(args.seed + b0)
        t0 = dt.datetime.now(dt.timezone.utc); tt = time.time()
        with torch.no_grad():
            out = model.generate(**enc, **gen_kw)
        lat = time.time() - tt
        t1 = dt.datetime.now(dt.timezone.utc)
        gen = out[:, enc['input_ids'].shape[1]:]
        for i, (((s, c), it), prompt) in enumerate(zip(batch, prompts)):
            ids = gen[i].tolist()
            n_out, hit_eos = 0, False
            for t in ids:
                if t in eos:
                    n_out += 1; hit_eos = True; break
                if t == tok.pad_token_id:
                    break
                n_out += 1
            text = tok.decode(ids[:n_out], skip_special_tokens=True).strip()
            n_in = int(enc['attention_mask'][i].sum())
            pred, how = parse_answer(text, it['options_en'].keys(), c)
            rec = dict(uid=it['uid'], source=it['source'], script=s, cond=c, gold=it['answer'], pred=pred,
                       correct=pred == it['answer'], parse=how,
                       ur_question_fixed=it.get('ur_question_fixed', False) if s == 'ur' else None,
                       response=text, finish_reason='stop' if hit_eos else 'length',
                       model=args.tag, model_version=f'{args.model_id}@{rev}', response_id=None,
                       usage={'promptTokenCount': n_in, 'candidatesTokenCount': n_out, 'thoughtsTokenCount': 0,
                              'totalTokenCount': n_in + n_out},
                       temperature=args.temperature,
                       thinking_level='disabled (enable_thinking=False)' if 'qwen' in args.model_id.lower() else None,
                       thinking_budget=None, retries=0, prompt=prompt, provider='hf-transformers',
                       reasoning_effort=None, temperature_sent=args.temperature, max_tokens=args.max_tokens,
                       errors=[], system_fingerprint=f'transformers {transformers.__version__}, torch {torch.__version__}, {hw}',
                       service_tier=None, refusal=None, quantization=args.quant, dtype=args.dtype, hf_model_id=args.model_id,
                       sampling=dict(do_sample=gen_kw.get('do_sample'), top_p=gen_kw.get('top_p'), top_k=gen_kw.get('top_k'), seed=args.seed + b0),
                       ur_question_truncated_in_original=it.get('ur_question_truncated_in_original', it.get('ur_truncated')) if s == 'ur' else None,
                       latency_s=round(lat / len(batch), 3), batch_latency_s=round(lat, 3), batch_size=len(batch),
                       t_start=t0.isoformat(), t_end=t1.isoformat(), parser_version=PARSER_VERSION)
            with open(jobs[(s, c)][0], 'a') as f:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            n_ok += 1
        el = time.time() - t_all
        print(f'{n_ok}/{len(order)} done | batch {len(batch)} in {lat:.1f}s | elapsed {el/60:.1f} min | '
              f'ETA {(len(order)-n_ok)*el/n_ok/60:.1f} min | last: {s}/{c} gold={it["answer"]} pred={pred} ({how})', flush=True)
    print('done;', n_ok, 'calls')


if __name__ == '__main__':
    run_local_hf_main()
