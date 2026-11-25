"""Build the parallel EN / Roman Urdu / Urdu item table from U-MIRAGE + MIRAGE and draw the
stratified 1,000-item subset (seed 42).

Inputs:
  umirage/benchmark_ru_translated.csv  (github.com/AliFaheem/U-Mirage @ 1f3a51d)
  mirage_benchmark.json                (github.com/Teddy-XiongGZ/MIRAGE benchmark.json: ids, sources, gold answers, EN options)
Outputs:
  data/items_all.jsonl   one row per MIRAGE item that has a U-MIRAGE translation
  data/subset_ids.csv    the 1,000 items everyone runs (source, mirage_id, answer, flags)
  data/subset_items.jsonl full text for the subset
"""
import ast, json, os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N_TARGET, SEED = 1000, 42
END = ('۔', '?', '؟', '.', '!', ':', '٭')

csv = pd.read_csv(os.path.join(ROOT, 'umirage/benchmark_ru_translated.csv'))
mir = json.load(open(os.path.join(ROOT, 'mirage_benchmark.json')))
q2id = {}
for src, recs in mir.items():
    for qid, r in recs.items():
        q2id.setdefault(r['question'], []).append((src, qid))

rows, seen = [], set()
for _, r in csv.iterrows():
    q = r['question_en']
    if not isinstance(q, str) or q not in q2id:
        continue
    try:
        ru_opts = ast.literal_eval(r['options_en'])  # column is mis-named: it holds the Roman Urdu options
    except Exception:
        continue
    for src, qid in q2id[q]:
        key = f'{src}-{qid}'
        if key in seen:
            continue
        m = mir[src][qid]
        if not isinstance(ru_opts, dict) or sorted(ru_opts) != sorted(m['options']):
            continue  # option letters must line up with the English item
        seen.add(key)
        ur = str(r['urdu']).strip()
        rows.append(dict(
            uid=key, source=src, mirage_id=qid, answer=m['answer'],
            n_options=len(m['options']),
            question_en=m['question'], options_en=m['options'],
            question_ru=str(r['roman_urdu']).strip(), options_ru=ru_opts,
            question_ur=ur,
            ur_maybe_truncated=bool(not ur.endswith(END)),
            ru_len=len(str(r['roman_urdu'])),
        ))

allf = pd.DataFrame(rows)
# drop pathological Roman Urdu rows (e.g. a 98k-char runaway generation)
allf['ru_bad'] = allf.ru_len > 4 * allf.question_en.str.len() + 200
print('matched unique items:', len(allf), '| ru_bad:', int(allf.ru_bad.sum()))
print(allf.source.value_counts().to_dict())
with open(os.path.join(ROOT, 'data/items_all.jsonl'), 'w') as f:
    for r in allf.to_dict('records'):
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

# proportional allocation to MIRAGE's own source sizes (largest-remainder), sampling from clean items
pool = allf[~allf.ru_bad]
sizes = {s: len(v) for s, v in mir.items()}
tot = sum(sizes.values())
raw = {s: N_TARGET * n / tot for s, n in sizes.items()}
alloc = {s: int(np.floor(x)) for s, x in raw.items()}
for s in sorted(raw, key=lambda s: raw[s] - alloc[s], reverse=True)[:N_TARGET - sum(alloc.values())]:
    alloc[s] += 1
rng = np.random.RandomState(SEED)
parts = []
for s in sorted(alloc):
    g = pool[pool.source == s].sort_values('uid')
    idx = rng.choice(len(g), size=alloc[s], replace=False)
    parts.append(g.iloc[np.sort(idx)])
sub = pd.concat(parts).reset_index(drop=True)
print('subset:', sub.source.value_counts().to_dict(), 'UR maybe truncated:', int(sub.ur_maybe_truncated.sum()))
sub[['uid', 'source', 'mirage_id', 'answer', 'n_options', 'ur_maybe_truncated']].to_csv(
    os.path.join(ROOT, 'data/subset_ids.csv'), index=False)
with open(os.path.join(ROOT, 'data/subset_items.jsonl'), 'w') as f:
    for r in sub.to_dict('records'):
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
