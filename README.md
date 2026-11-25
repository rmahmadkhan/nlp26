# NLP project: U-MIRAGE RQ1 replication package ("Do LLMs Understand Medical Questions Across Urdu Scripts?")

## 1. Purpose and research question
This package re-runs the core comparison of **U-MIRAGE** (Urdu medical QA) on newer models. **RQ1:** do LLMs answer the same health
multiple-choice questions less accurately in **Urdu script (UR)** than in **English (EN)** and **Roman Urdu (RU)**?
We use U-MIRAGE's two prompts, zero-shot (`zs`) and its "CoT" prompt (`umcot`, which asks the model to reason but still return only the letter).
We test six models: three API models that succeed the paper's API rows, and three small open models that succeed its small-model rows.

What we report: accuracy per language × prompt with 95% bootstrap CIs; paired EN-RU, EN-UR and RU-UR gaps with 95% bootstrap CIs
(10,000 resamples) and exact McNemar tests; EN vs UR on Urdu questions that are truncated vs complete in the U-MIRAGE release;
answer-format compliance (parse failures, non-bare-letter replies, length cut-offs). Every model sees the same
random sample of 366 of U-MIRAGE's 7,663 questions (seed 42), sized for 95% confidence and a 5% margin of error
(Cochran's formula with the finite-population correction). That is 2,196 calls per model.

Everything a reviewer needs is included: inputs, the full raw output of every model call, the code, expected values, and executed notebooks.

## 2. Quick start: check our numbers (no keys, no GPU, no network, about 10 s)
```
pip install -r requirements.txt
python scripts/reproduce_tables.py
```
This rebuilds every results table for all six models from the raw outputs in `results/`. It also recomputes accuracies, n, parse
failures, gaps, McNemar counts and p-values, and the truncation split independently, and asserts they match `expected_results.json`.
It prints the accuracy table and `PASS`, and exits 0.
The same check is the default `MODE = 'score_only'` of `notebooks/nlp_project_api_models.ipynb` (Colab or local Jupyter: *Run all*).
An executed copy ending in PASS is in `notebooks/executed/`.

## 2b. Main results in brief (full tables in §8, caveats in §9)
- In zero-shot, Urdu script scores lowest of the three scripts for all six models, 7–24 percentage points below English
  (EN−UR, exact McNemar p < 0.02 for every model). For Qwen3.5 0.8B, Urdu is only 0.5 points behind Roman Urdu (a tie in practice).
- The API successors match or beat the paper's API rows. U-MIRAGE's CoT prompt narrows the Urdu gap for the Gemini-API models, but not for GPT-6 Luna.
- Among the small models, Qwen3.5 0.8B beats the paper's Qwen 2.5 0.5B in zero-shot (40/33/33% vs 26/24/23% EN/RU/UR). Llama 3.2 1B in bf16
  scores below the paper's full-precision row (38/29/21% vs 45/34/34%). The CoT prompt does not help any small model.
- Caveats that affect specific cells: Qwen's Roman-Urdu CoT has 21.3% parse failures (§9.7), and parse-failure counts for the small
  models differ between stored and scored values without changing accuracy (§9.8).

## 3. Folder layout
```
README.md                         this file
expected_results.json             reported numbers (all 6 models) checked by scripts/reproduce_tables.py
requirements.txt                  scoring, table reproduction and API runs (pinned)
requirements-gpu.txt              small-model GPU runs (pinned)
requirements-notebook.txt         running the notebooks locally
SHA256SUMS.txt                    checksums of every file in the package
DATA_LICENSE_AND_ATTRIBUTION.md, LICENSE-U-MIRAGE.txt, CITATION-U-MIRAGE.cff   data provenance and licences
notebooks/nlp_project_api_models.ipynb     score-only check of all 6 models [default], or re-run the 3 API models
notebooks/nlp_project_small_models.ipynb   re-run the 3 small models on a Colab GPU, then score them
notebooks/executed/nlp_project_small_models_executed.ipynb        our actual Colab GPU run, with all outputs
notebooks/executed/nlp_project_api_models_score_only_executed.ipynb   score-only check, with outputs (PASS)
notebooks/README_notebooks.md     notebook details
scripts/                          the same code as the notebooks, for command-line use
data/                             the 1,000-item subset, the 366 sample ids, generated Urdu options, re-translated questions
share/nlp_project_sample366.{jsonl,csv}   the 366 evaluation items (all fields the runners use)
results/<model>/<script>_<cond>.jsonl        full raw records, one JSON line per model call (6 models × 6 files × 366)
results/<model>/scores_sample366.md, scores_extra_sample366.md   per-model scores
results/summary_all_models_sample366.md      combined table for all 6 models (+ all paper rows)
results/summary_api_models_sample366.md, summary_small_models_sample366.md   per-group tables
smoke_results_colab/<tag>/        5-item smoke test from our Colab run (not used in any table)
logs/                             console logs of the original API runs
```
`<script>` is `en`, `ru` or `ur`. `<cond>` is `zs` or `umcot`. Model folders: `gpt-6-luna`, `gemma-4-26b-a4b-it`, `gemini-3.5-flash-lite`,
`qwen3.5-0.8b-bnb4`, `llama3.2-1b-instruct-bnb4`, `llama3.2-1b-instruct-bf16`.

## 4. What each notebook and script does
**Notebooks** hold their code as readable cells (copied verbatim from `scripts/`), with a short "Step N" note before each code cell
saying what it does, what it reads and what it writes. Only data is loaded, from `DATA_DIR`, a folder with `share/`, `data/`, `results/`
and `expected_results.json` (this package root has that layout).
- `notebooks/nlp_project_api_models.ipynb`: `MODE = 'score_only'` (default) runs the reproduction check for all six models.
  `MODE = 'run'` re-runs GPT-6 Luna, Gemma 4 26B-A4B and Gemini 3.5 Flash-Lite with our exact settings into `results_rerun/`, then scores them.
- `notebooks/nlp_project_small_models.ipynb`: on a GPU, runs Qwen3.5 0.8B (NF4), Llama 3.2 1B Instruct (NF4) and Llama 3.2 1B
  Instruct (bf16) into `results_rerun/`, then scores them against the paper's small-model rows.

**Scripts**
```
scripts/run_eval.py          API runner (OpenAI / Gemini). U-MIRAGE Figure 1 prompts verbatim, answer parser (v2), resumable, retries, cost cap
scripts/run_local_hf.py      Hugging Face transformers runner: same prompts, parser and record format; NF4 or bf16/fp16; resumable
scripts/score.py             per-model scores: accuracy, source-weighted accuracy, paired gaps + bootstrap CI + McNemar, per-dataset, reply script
scripts/score_extra.py       paper-style table + CIs, gap table, truncated-vs-complete Urdu split, compliance, U-MIRAGE paper reference rows
scripts/reproduce_tables.py  one-click regeneration of all tables + assertion against expected_results.json
scripts/prepare_data.py      builds the 1,000-item subset from U-MIRAGE + MIRAGE (needs both source repos)
scripts/fix_urdu.py, fix_urdu_v2.py   Urdu-script option generation / question re-translation (gemini-3.5-flash-lite)
scripts/batch_eval.py        Gemini Batch API helper (not used for the reported results)
```
Record fields include `uid, source, script, cond, gold, pred, correct, parse, response, finish_reason, model, model_version, usage,
temperature, thinking_level, reasoning_effort, max_tokens, prompt, errors, retries, ur_question_truncated_in_original, latency_s, t_start, t_end`.
The small-model records also have `hf_model_id, quantization, dtype, sampling, system_fingerprint` (library versions and GPU).
`pred`/`correct` as stored come from the parser at run time. **All tables re-parse `response` with parser v2 and the letters A-D** (see §9.8).

## 5. Data provenance and licence
Items are MIRAGE medical MCQs (MMLU-Med, MedQA-US, MedMCQA, PubMedQA*, BioASQ-Y/N; English questions, options and gold answers from
https://github.com/Teddy-XiongGZ/MIRAGE). The Roman Urdu questions/options and the Urdu-script questions come verbatim from U-MIRAGE
(https://github.com/AliFaheem/U-Mirage, MIT licence; `benchmark_ru_translated.csv`). We generated only the Urdu-script options that
the release lacks (§9.3). See `DATA_LICENSE_AND_ATTRIBUTION.md`, `LICENSE-U-MIRAGE.txt` and `CITATION-U-MIRAGE.cff`. Please cite U-MIRAGE and MIRAGE.

## 6. Models and settings
All runs: sample `share/nlp_project_sample366.jsonl`, original (released) Urdu questions (`--ur-original-questions`), scripts en/ru/ur,
conditions `zs` and `umcot`, temperature 0.1, max 2,048 output tokens, seed 42 (API runs interleaved and shuffled with seed 42).

| model (folder) | provider / weights | reasoning / precision | concurrency | run (UTC) | cost |
|---|---|---|---|---|---|
| `gpt-6-luna` | OpenAI Chat Completions | `reasoning_effort: none` | 900 rpm / 16 workers | 2026-11-23 17:10–17:14 | ~$0.04 |
| `gemma-4-26b-a4b-it` | Gemini API `generateContent` | `thinkingLevel: minimal` | 28 rpm / 6 workers, timeout 120 s | 2026-11-23 17:26 – 11-24 00:41 (resumed after billing stops) | ~$0.23 |
| `gemini-3.5-flash-lite` | Gemini API `generateContent` | `thinkingLevel: minimal` | 60 rpm / 4 workers | 2026-11-24 01:34–02:11 | ~$0.87 |
| `qwen3.5-0.8b-bnb4` | `Qwen/Qwen3.5-0.8B` @ `2fc06364715b967f1860aea9cf38778875588b17` | bitsandbytes 4-bit NF4 (bf16 compute); thinking disabled | batch 32 | 2026-11-24 10:37–11:53 | Colab |
| `llama3.2-1b-instruct-bnb4` | `meta-llama/Llama-3.2-1B-Instruct` @ `9213176726f574b556790deb65791e0c5aa438b6` | bitsandbytes 4-bit NF4 (bf16 compute) | batch 32 | 2026-11-24 11:53–11:56 | Colab |
| `llama3.2-1b-instruct-bf16` | same as above | bf16, no quantization | batch 32 | 2026-11-24 11:56–12:01 | Colab |

The APIs return no snapshot/version beyond these IDs. API costs are estimated from logged token usage. Small models ran on Google Colab with an
**NVIDIA L4** (bf16 supported, so the full-precision row is true bf16, not fp16), transformers 5.24.0, torch 2.14.1+cu130, bitsandbytes 0.50.2.
Sampling: `do_sample=True`, temperature 0.1, top_p 1.0, top_k 0, seed 42. The HF revisions above are pinned in every record (`model_version`).

## 7. How to reproduce
**(a) Score only (recommended for review).** §2 above: `python scripts/reproduce_tables.py`, or open
`notebooks/nlp_project_api_models.ipynb` and *Run all* (default `MODE = 'score_only'`). Ways to give a notebook the data:
- *Local Jupyter:* run from the package root or `notebooks/`; the data is found automatically. Headless:
  `jupyter nbconvert --to notebook --execute notebooks/nlp_project_api_models.ipynb --output check_executed.ipynb`
- *Colab, Files tab:* upload `nlp_project_data.zip` (data only, distributed next to this package) when the notebook asks; or drag it into the
  **Files** tab and run `!unzip -q /content/nlp_project_data.zip -d /content` (gives `/content/nlp_project_data`, found automatically).
- *Colab, Google Drive:* unzip it into Drive and set `DATA_DIR = '/content/drive/MyDrive/nlp_project_data'`. The notebook mounts Drive.

**(b) Re-run the API models.** In the API notebook set `MODE = 'run'` and add `OPENAI_API_KEY` and/or `GEMINI_API_KEY` as Colab secrets or
environment variables. Keys are never printed or saved. Output goes to `results_rerun/`, and re-running resumes. `SMOKE_ITEMS = 2` makes
a tiny paid test first. Full cost at our settings is about $1.15. Expect small differences: temperature is 0.1, not 0, and hosted
models can change behind the same ID. CLI equivalent: `python scripts/run_eval.py ...` (exact flags are in the notebook's settings cell
and in `logs/`).

**(c) Re-run the small models (Colab GPU).** Open `notebooks/nlp_project_small_models.ipynb`, choose *Runtime > Change runtime type > GPU*
(L4 or A100 recommended), accept the Llama 3.2 licence on Hugging Face, add `HF_TOKEN` as a Colab secret, put the data on Drive (option above,
so results survive disconnects), then *Run all*. Our run took 84 min on an L4: Qwen 75 min, mostly long Roman-Urdu CoT replies, and Llama about 3–5 min each.
Results go to `results_rerun/<tag>/` and are scored at the end. Sampling is stochastic (temperature 0.1), so expect small differences
from our numbers. Our executed run is in `notebooks/executed/nlp_project_small_models_executed.ipynb`.

## 8. Expected results (366 items; paper rows are U-MIRAGE's full 7,663-item benchmark)
**Paper rows vs our successors** (accuracy in %, 2 decimals; each U-MIRAGE row sits directly above the model we ran in its place).
[paper] = U-MIRAGE, full benchmark (7,663 items); [ours] = our random 366-item sample (seed 42), so rows are comparable in level but not
item-matched. Gemma 4 26B-A4B is **not size-matched** to Gemma 2 2B (26B total / ~4B active parameters vs 2B).
The paper's "LLaMA 3.2 1B (q)" row is Ollama Q8_0, ours is NF4 (§9.5).

| Model | EN ZS | EN CoT | RU ZS | RU CoT | UR ZS | UR CoT |
|---|---|---|---|---|---|---|
| GPT-5 nano [paper] | 79.62 | 78.65 | 75.02 | 74.98 | 72.99 | 70.23 |
| GPT-6 Luna [ours] | 81.69 | 82.24 | 79.51 | 80.05 | 74.86 | 74.86 |
| Gemini 2.0 Flash-Lite [paper] | 71.77 | 77.79 | 65.82 | 74.14 | 67.68 | 70.13 |
| Gemini 3.5 Flash-Lite [ours] | 82.79 | 84.15 | 78.42 | 79.78 | 69.13 | 77.05 |
| Gemma 2 2B [paper] | 41.98 | 43.25 | 32.47 | 35.00 | 31.24 | 33.67 |
| Gemma 4 26B-A4B [ours] | 77.60 | 80.60 | 68.03 | 69.95 | 53.28 | 63.93 |
| Qwen 2.5 0.5B (q) [paper] | 25.92 | 29.74 | 23.78 | 27.65 | 23.05 | 27.21 |
| Qwen3.5 0.8B (q, NF4) [ours] | 40.16 | 36.07 | 33.33 | 27.05 | 32.79 | 32.79 |
| LLaMA 3.2 1B (q) [paper] | 18.86 | 38.89 | 19.82 | 24.00 | 18.83 | 17.81 |
| Llama 3.2 1B Instruct (q, NF4) [ours] | 35.52 | 33.06 | 36.07 | 31.42 | 26.23 | 23.50 |
| LLaMA 3.2 1B [paper] | 45.49 | 44.37 | 34.48 | 36.16 | 33.64 | 31.24 |
| Llama 3.2 1B Instruct (bf16) [ours] | 38.25 | 25.68 | 28.69 | 30.60 | 21.04 | 18.31 |

Paper-style table (fraction correct, 2 decimals), "CoT" = U-MIRAGE's CoT prompt (`umcot`):

| Model | EN Zero-Shot | EN CoT | RU Zero-Shot | RU CoT | UR Zero-Shot | UR CoT |
|---|---|---|---|---|---|---|
| GPT-6 Luna | 0.82 | 0.82 | 0.80 | 0.80 | 0.75 | 0.75 |
| Gemma 4 26B-A4B | 0.78 | 0.81 | 0.68 | 0.70 | 0.53 | 0.64 |
| Gemini 3.5 Flash-Lite | 0.83 | 0.84 | 0.78 | 0.80 | 0.69 | 0.77 |
| Qwen3.5 0.8B (q, NF4) | 0.40 | 0.36 | 0.33 | 0.27 | 0.33 | 0.33 |
| Llama 3.2 1B Instruct (q, NF4) | 0.36 | 0.33 | 0.36 | 0.31 | 0.26 | 0.23 |
| Llama 3.2 1B Instruct (bf16) | 0.38 | 0.26 | 0.29 | 0.31 | 0.21 | 0.18 |
| *U-MIRAGE paper reference rows (full benchmark, 7,663 items):* | | | | | | |
| GPT-5 nano [paper] | 0.80 | 0.79 | 0.75 | 0.75 | 0.73 | 0.70 |
| Gemini 2.0 Flash-Lite [paper] | 0.72 | 0.78 | 0.66 | 0.74 | 0.68 | 0.70 |
| Gemma 2 2B [paper] | 0.42 | 0.43 | 0.32 | 0.35 | 0.31 | 0.34 |
| Qwen 2.5 0.5B (q) [paper] | 0.26 | 0.30 | 0.24 | 0.28 | 0.23 | 0.27 |
| LLaMA 3.2 1B (q) [paper] | 0.19 | 0.39 | 0.20 | 0.24 | 0.19 | 0.18 |
| LLaMA 3.2 1B [paper] | 0.45 | 0.44 | 0.34 | 0.36 | 0.34 | 0.31 |

Accuracy in % (2 decimals):

| Model | EN ZS | EN CoT | RU ZS | RU CoT | UR ZS | UR CoT |
|---|---|---|---|---|---|---|
| GPT-6 Luna | 81.69 | 82.24 | 79.51 | 80.05 | 74.86 | 74.86 |
| Gemma 4 26B-A4B | 77.60 | 80.60 | 68.03 | 69.95 | 53.28 | 63.93 |
| Gemini 3.5 Flash-Lite | 82.79 | 84.15 | 78.42 | 79.78 | 69.13 | 77.05 |
| Qwen3.5 0.8B (q, NF4) | 40.16 | 36.07 | 33.33 | 27.05 | 32.79 | 32.79 |
| Llama 3.2 1B Instruct (q, NF4) | 35.52 | 33.06 | 36.07 | 31.42 | 26.23 | 23.50 |
| Llama 3.2 1B Instruct (bf16) | 38.25 | 25.68 | 28.69 | 30.60 | 21.04 | 18.31 |

Accuracy with 95% bootstrap CI (10,000 resamples):

| Model | EN ZS | EN CoT | RU ZS | RU CoT | UR ZS | UR CoT |
|---|---|---|---|---|---|---|
| GPT-6 Luna | 0.82 [0.78, 0.86] | 0.82 [0.78, 0.86] | 0.80 [0.75, 0.84] | 0.80 [0.76, 0.84] | 0.75 [0.70, 0.79] | 0.75 [0.70, 0.79] |
| Gemma 4 26B-A4B | 0.78 [0.73, 0.82] | 0.81 [0.76, 0.85] | 0.68 [0.63, 0.73] | 0.70 [0.65, 0.75] | 0.53 [0.48, 0.58] | 0.64 [0.59, 0.69] |
| Gemini 3.5 Flash-Lite | 0.83 [0.79, 0.87] | 0.84 [0.80, 0.88] | 0.78 [0.74, 0.83] | 0.80 [0.76, 0.84] | 0.69 [0.64, 0.74] | 0.77 [0.73, 0.81] |
| Qwen3.5 0.8B (q, NF4) | 0.40 [0.35, 0.45] | 0.36 [0.31, 0.41] | 0.33 [0.28, 0.38] | 0.27 [0.22, 0.32] | 0.33 [0.28, 0.38] | 0.33 [0.28, 0.38] |
| Llama 3.2 1B Instruct (q, NF4) | 0.36 [0.31, 0.40] | 0.33 [0.28, 0.38] | 0.36 [0.31, 0.41] | 0.31 [0.27, 0.36] | 0.26 [0.22, 0.31] | 0.23 [0.19, 0.28] |
| Llama 3.2 1B Instruct (bf16) | 0.38 [0.33, 0.43] | 0.26 [0.21, 0.30] | 0.29 [0.24, 0.33] | 0.31 [0.26, 0.35] | 0.21 [0.17, 0.25] | 0.18 [0.14, 0.22] |

Paired gaps (accuracy %, diff in percentage points, 95% bootstrap CI, exact McNemar):

| model | cond | pair | n | acc 1st | acc 2nd | diff | 95% CI | b01/b10 | McNemar p |
|---|---|---|---|---|---|---|---|---|---|
| GPT-6 Luna | zs | EN-RU | 366 | 81.69 | 79.51 | +2.19 | [-1.09, +5.46] | 24/16 | 0.268 |
| GPT-6 Luna | zs | EN-UR | 366 | 81.69 | 74.86 | +6.83 | [+3.01, +10.93] | 40/15 | 0.00102 |
| GPT-6 Luna | zs | RU-UR | 366 | 79.51 | 74.86 | +4.64 | [+0.55, +8.74] | 38/21 | 0.0363 |
| GPT-6 Luna | umcot | EN-RU | 366 | 82.24 | 80.05 | +2.19 | [-1.09, +5.46] | 23/15 | 0.256 |
| GPT-6 Luna | umcot | EN-UR | 366 | 82.24 | 74.86 | +7.38 | [+3.55, +11.20] | 38/11 | 0.000142 |
| GPT-6 Luna | umcot | RU-UR | 366 | 80.05 | 74.86 | +5.19 | [+1.37, +9.29] | 37/18 | 0.0145 |
| Gemma 4 26B-A4B | zs | EN-RU | 366 | 77.60 | 68.03 | +9.56 | [+4.64, +14.21] | 59/24 | 0.000155 |
| Gemma 4 26B-A4B | zs | EN-UR | 366 | 77.60 | 53.28 | +24.32 | [+18.85, +29.78] | 110/21 | 9.43e-16 |
| Gemma 4 26B-A4B | zs | RU-UR | 366 | 68.03 | 53.28 | +14.75 | [+9.56, +20.22] | 79/25 | 1.05e-07 |
| Gemma 4 26B-A4B | umcot | EN-RU | 366 | 80.60 | 69.95 | +10.66 | [+6.01, +15.30] | 62/23 | 2.77e-05 |
| Gemma 4 26B-A4B | umcot | EN-UR | 366 | 80.60 | 63.93 | +16.67 | [+11.48, +22.13] | 84/23 | 2.4e-09 |
| Gemma 4 26B-A4B | umcot | RU-UR | 366 | 69.95 | 63.93 | +6.01 | [+1.37, +10.93] | 52/30 | 0.0198 |
| Gemini 3.5 Flash-Lite | zs | EN-RU | 366 | 82.79 | 78.42 | +4.37 | [+0.55, +8.20] | 35/19 | 0.0402 |
| Gemini 3.5 Flash-Lite | zs | EN-UR | 366 | 82.79 | 69.13 | +13.66 | [+9.02, +18.31] | 65/15 | 1.41e-08 |
| Gemini 3.5 Flash-Lite | zs | RU-UR | 366 | 78.42 | 69.13 | +9.29 | [+4.92, +13.66] | 53/19 | 7.56e-05 |
| Gemini 3.5 Flash-Lite | umcot | EN-RU | 366 | 84.15 | 79.78 | +4.37 | [+1.09, +7.65] | 26/10 | 0.0113 |
| Gemini 3.5 Flash-Lite | umcot | EN-UR | 366 | 84.15 | 77.05 | +7.10 | [+3.28, +10.93] | 38/12 | 0.000306 |
| Gemini 3.5 Flash-Lite | umcot | RU-UR | 366 | 79.78 | 77.05 | +2.73 | [-0.82, +6.28] | 29/19 | 0.193 |
| Qwen3.5 0.8B (q, NF4) | zs | EN-RU | 366 | 40.16 | 33.33 | +6.83 | [+2.19, +11.48] | 49/24 | 0.00463 |
| Qwen3.5 0.8B (q, NF4) | zs | EN-UR | 366 | 40.16 | 32.79 | +7.38 | [+1.91, +12.84] | 68/41 | 0.0124 |
| Qwen3.5 0.8B (q, NF4) | zs | RU-UR | 366 | 33.33 | 32.79 | +0.55 | [-4.64, +5.74] | 47/45 | 0.917 |
| Qwen3.5 0.8B (q, NF4) | umcot | EN-RU | 366 | 36.07 | 27.05 | +9.02 | [+2.73, +15.03] | 82/49 | 0.00498 |
| Qwen3.5 0.8B (q, NF4) | umcot | EN-UR | 366 | 36.07 | 32.79 | +3.28 | [-1.64, +8.20] | 49/37 | 0.235 |
| Qwen3.5 0.8B (q, NF4) | umcot | RU-UR | 366 | 27.05 | 32.79 | -5.74 | [-11.20, +0.00] | 48/69 | 0.064 |
| Llama 3.2 1B Instruct (q, NF4) | zs | EN-RU | 366 | 35.52 | 36.07 | -0.55 | [-5.19, +4.10] | 37/39 | 0.909 |
| Llama 3.2 1B Instruct (q, NF4) | zs | EN-UR | 366 | 35.52 | 26.23 | +9.29 | [+3.01, +15.30] | 86/52 | 0.00479 |
| Llama 3.2 1B Instruct (q, NF4) | zs | RU-UR | 366 | 36.07 | 26.23 | +9.84 | [+3.55, +16.12] | 87/51 | 0.00275 |
| Llama 3.2 1B Instruct (q, NF4) | umcot | EN-RU | 366 | 33.06 | 31.42 | +1.64 | [-2.19, +5.74] | 31/25 | 0.504 |
| Llama 3.2 1B Instruct (q, NF4) | umcot | EN-UR | 366 | 33.06 | 23.50 | +9.56 | [+4.37, +14.75] | 65/30 | 0.000425 |
| Llama 3.2 1B Instruct (q, NF4) | umcot | RU-UR | 366 | 31.42 | 23.50 | +7.92 | [+2.73, +13.11] | 63/34 | 0.00423 |
| Llama 3.2 1B Instruct (bf16) | zs | EN-RU | 366 | 38.25 | 28.69 | +9.56 | [+4.10, +14.75] | 69/34 | 0.000728 |
| Llama 3.2 1B Instruct (bf16) | zs | EN-UR | 366 | 38.25 | 21.04 | +17.21 | [+10.66, +23.50] | 111/48 | 6.35e-07 |
| Llama 3.2 1B Instruct (bf16) | zs | RU-UR | 366 | 28.69 | 21.04 | +7.65 | [+2.19, +13.11] | 67/39 | 0.00842 |
| Llama 3.2 1B Instruct (bf16) | umcot | EN-RU | 366 | 25.68 | 30.60 | -4.92 | [-11.75, +2.19] | 76/94 | 0.192 |
| Llama 3.2 1B Instruct (bf16) | umcot | EN-UR | 366 | 25.68 | 18.31 | +7.38 | [+0.82, +13.66] | 85/58 | 0.0293 |
| Llama 3.2 1B Instruct (bf16) | umcot | RU-UR | 366 | 30.60 | 18.31 | +12.30 | [+6.83, +18.03] | 80/35 | 3.28e-05 |

Urdu questions truncated in the U-MIRAGE release (70 of 366) vs complete (296), EN vs UR on the same items:

| model | cond | subset | n | UR acc | EN acc | EN-UR | 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|---|
| GPT-6 Luna | zs | truncated | 70 | 64.29 | 85.71 | +21.43 | [+12.86, +31.43] | 6.1e-05 |
| GPT-6 Luna | zs | complete | 296 | 77.36 | 80.74 | +3.38 | [-0.68, +7.43] | 0.154 |
| GPT-6 Luna | umcot | truncated | 70 | 67.14 | 87.14 | +20.00 | [+8.57, +31.43] | 0.00131 |
| GPT-6 Luna | umcot | complete | 296 | 76.69 | 81.08 | +4.39 | [+0.68, +8.11] | 0.0294 |
| Gemma 4 26B-A4B | zs | truncated | 70 | 44.29 | 90.00 | +45.71 | [+34.29, +57.14] | 4.07e-09 |
| Gemma 4 26B-A4B | zs | complete | 296 | 55.41 | 74.66 | +19.26 | [+13.18, +25.68] | 4.59e-09 |
| Gemma 4 26B-A4B | umcot | truncated | 70 | 60.00 | 88.57 | +28.57 | [+17.14, +40.00] | 1.1e-05 |
| Gemma 4 26B-A4B | umcot | complete | 296 | 64.86 | 78.72 | +13.85 | [+7.77, +19.93] | 9.81e-06 |
| Gemini 3.5 Flash-Lite | zs | truncated | 70 | 57.14 | 92.86 | +35.71 | [+24.29, +47.14] | 5.96e-08 |
| Gemini 3.5 Flash-Lite | zs | complete | 296 | 71.96 | 80.41 | +8.45 | [+3.72, +13.18] | 0.00102 |
| Gemini 3.5 Flash-Lite | umcot | truncated | 70 | 71.43 | 92.86 | +21.43 | [+12.86, +31.43] | 6.1e-05 |
| Gemini 3.5 Flash-Lite | umcot | complete | 296 | 78.38 | 82.09 | +3.72 | [-0.34, +7.77] | 0.0895 |
| Qwen3.5 0.8B (q, NF4) | zs | truncated | 70 | 24.29 | 32.86 | +8.57 | [-5.71, +22.86] | 0.327 |
| Qwen3.5 0.8B (q, NF4) | zs | complete | 296 | 34.80 | 41.89 | +7.09 | [+1.01, +13.18] | 0.0275 |
| Qwen3.5 0.8B (q, NF4) | umcot | truncated | 70 | 31.43 | 38.57 | +7.14 | [-4.29, +18.57] | 0.359 |
| Qwen3.5 0.8B (q, NF4) | umcot | complete | 296 | 33.11 | 35.47 | +2.36 | [-3.04, +7.77] | 0.464 |
| Llama 3.2 1B Instruct (q, NF4) | zs | truncated | 70 | 20.00 | 24.29 | +4.29 | [-7.14, +15.71] | 0.629 |
| Llama 3.2 1B Instruct (q, NF4) | zs | complete | 296 | 27.70 | 38.18 | +10.47 | [+3.38, +17.91] | 0.00615 |
| Llama 3.2 1B Instruct (q, NF4) | umcot | truncated | 70 | 32.86 | 31.43 | -1.43 | [-12.86, +10.00] | 1 |
| Llama 3.2 1B Instruct (q, NF4) | umcot | complete | 296 | 21.28 | 33.45 | +12.16 | [+6.42, +17.91] | 5.57e-05 |
| Llama 3.2 1B Instruct (bf16) | zs | truncated | 70 | 17.14 | 35.71 | +18.57 | [+4.29, +32.86] | 0.0192 |
| Llama 3.2 1B Instruct (bf16) | zs | complete | 296 | 21.96 | 38.85 | +16.89 | [+9.80, +24.32] | 1.61e-05 |
| Llama 3.2 1B Instruct (bf16) | umcot | truncated | 70 | 18.57 | 34.29 | +15.71 | [+0.00, +31.43] | 0.0895 |
| Llama 3.2 1B Instruct (bf16) | umcot | complete | 296 | 18.24 | 23.65 | +5.41 | [-1.35, +12.16] | 0.149 |

Answer-format compliance (parse failures count as wrong):

| model | run | n | parse fail | zs not bare letter | hit max_tokens |
|---|---|---|---|---|---|
| GPT-6 Luna | en/zs | 366 | 0 (0.0%) | 0.0% | 0.0% |
| GPT-6 Luna | en/umcot | 366 | 0 (0.0%) | - | 0.0% |
| GPT-6 Luna | ru/zs | 366 | 0 (0.0%) | 0.0% | 0.0% |
| GPT-6 Luna | ru/umcot | 366 | 0 (0.0%) | - | 0.0% |
| GPT-6 Luna | ur/zs | 366 | 0 (0.0%) | 0.0% | 0.0% |
| GPT-6 Luna | ur/umcot | 366 | 0 (0.0%) | - | 0.0% |
| Gemma 4 26B-A4B | en/zs | 366 | 1 (0.3%) | 0.5% | 0.0% |
| Gemma 4 26B-A4B | en/umcot | 366 | 0 (0.0%) | - | 0.5% |
| Gemma 4 26B-A4B | ru/zs | 366 | 2 (0.5%) | 0.8% | 0.0% |
| Gemma 4 26B-A4B | ru/umcot | 366 | 3 (0.8%) | - | 1.1% |
| Gemma 4 26B-A4B | ur/zs | 366 | 1 (0.3%) | 0.5% | 0.0% |
| Gemma 4 26B-A4B | ur/umcot | 366 | 0 (0.0%) | - | 0.0% |
| Gemini 3.5 Flash-Lite | en/zs | 366 | 2 (0.5%) | 42.9% | 0.0% |
| Gemini 3.5 Flash-Lite | en/umcot | 366 | 0 (0.0%) | - | 0.0% |
| Gemini 3.5 Flash-Lite | ru/zs | 366 | 0 (0.0%) | 4.1% | 0.0% |
| Gemini 3.5 Flash-Lite | ru/umcot | 366 | 0 (0.0%) | - | 0.0% |
| Gemini 3.5 Flash-Lite | ur/zs | 366 | 2 (0.5%) | 7.4% | 0.0% |
| Gemini 3.5 Flash-Lite | ur/umcot | 366 | 0 (0.0%) | - | 0.0% |
| Qwen3.5 0.8B (q, NF4) | en/zs | 366 | 0 (0.0%) | 0.3% | 0.0% |
| Qwen3.5 0.8B (q, NF4) | en/umcot | 366 | 0 (0.0%) | - | 0.0% |
| Qwen3.5 0.8B (q, NF4) | ru/zs | 366 | 0 (0.0%) | 0.3% | 0.0% |
| Qwen3.5 0.8B (q, NF4) | ru/umcot | 366 | 78 (21.3%) | - | 5.5% |
| Qwen3.5 0.8B (q, NF4) | ur/zs | 366 | 0 (0.0%) | 0.0% | 0.0% |
| Qwen3.5 0.8B (q, NF4) | ur/umcot | 366 | 1 (0.3%) | - | 0.5% |
| Llama 3.2 1B Instruct (q, NF4) | en/zs | 366 | 0 (0.0%) | 8.7% | 0.0% |
| Llama 3.2 1B Instruct (q, NF4) | en/umcot | 366 | 0 (0.0%) | - | 0.0% |
| Llama 3.2 1B Instruct (q, NF4) | ru/zs | 366 | 0 (0.0%) | 9.0% | 0.0% |
| Llama 3.2 1B Instruct (q, NF4) | ru/umcot | 366 | 2 (0.5%) | - | 0.3% |
| Llama 3.2 1B Instruct (q, NF4) | ur/zs | 366 | 0 (0.0%) | 18.6% | 0.0% |
| Llama 3.2 1B Instruct (q, NF4) | ur/umcot | 366 | 0 (0.0%) | - | 0.0% |
| Llama 3.2 1B Instruct (bf16) | en/zs | 366 | 0 (0.0%) | 17.5% | 0.0% |
| Llama 3.2 1B Instruct (bf16) | en/umcot | 366 | 1 (0.3%) | - | 0.0% |
| Llama 3.2 1B Instruct (bf16) | ru/zs | 366 | 0 (0.0%) | 10.9% | 0.0% |
| Llama 3.2 1B Instruct (bf16) | ru/umcot | 366 | 18 (4.9%) | - | 0.5% |
| Llama 3.2 1B Instruct (bf16) | ur/zs | 366 | 0 (0.0%) | 1.9% | 0.0% |
| Llama 3.2 1B Instruct (bf16) | ur/umcot | 366 | 4 (1.1%) | - | 0.3% |

## 9. Known deviations from U-MIRAGE
1. **Sample:** a random sample of 366 items (seed 42), not the full 7,663. The paper rows are therefore indicative, not item-matched.
2. **Urdu questions kept as released:** about 19% of sample items (70/366) have Urdu questions cut off in U-MIRAGE's public CSV.
   We used them unchanged (`--ur-original-questions`) and report results split by truncation.
   Re-translated versions are in `data/questions_ur_fixed.jsonl` but were **not** used for the reported numbers.
3. **Urdu-script options generated by us:** the public release has no Urdu-script options, so we generated only these
   (`options_ur`, from Roman Urdu with English as reference). For the 366 sample items: 303 were generated by `gemini-3.5-flash-lite`
   with script validation, 57 are yes/no/maybe options from a fixed dictionary, 4 were corrected by hand after repeated validation failures,
   and 2 numeric option sets were kept identical to English (`ur_options_method` field). Questions and RU options are U-MIRAGE's own.
4. **Successor models:** GPT-6 Luna for GPT-5 nano, Gemini 3.5 Flash-Lite for Gemini 2.0 Flash-Lite, Gemma 4 26B-A4B for Gemma 2 2B,
   and Qwen3.5 0.8B for Qwen 2.5 0.5B. Llama 3.2 1B Instruct is the same model as the paper's, because Meta has released no newer ~1B Llama.
5. **Quantization and runtime:** our "q" rows use bitsandbytes 4-bit NF4 via Hugging Face transformers. The paper's Qwen "q" row used Ollama Q4_K_M,
   and its "LLaMA 3.2 1B q" row used Ollama's default `llama3.2:1b` tag, which is Q8_0. Our full-precision Llama row is bf16 on an L4.
6. **Decoding:** temperature 0.1, max 2,048 output tokens. Reasoning/thinking is set to the minimum each model allows: none for Luna,
   minimal for the Gemini-API models, disabled for Qwen3.5.
7. **Answer parsing:** a deterministic regex parser (`scripts/run_eval.py: parse_answer`, version 2) is applied to the raw replies at scoring time.
   Unparseable replies count as wrong and are reported as parse failures. For `umcot` the parser expects the final answer at the end.
   Qwen3.5's RU-CoT run has 78 parse failures (21.3%). 74 of those replies start with a letter and then give a long explanation with no
   final letter, and 18 of the 78 hit the 2,048-token limit. If those leading letters were accepted, Qwen's RU-CoT accuracy would be
   33.06% instead of 27.05%. The reported numbers do not do this; the raw replies are included to check.
8. **Stored vs scored parse (small models):** the runner stored `pred` using each item's valid letters (2 for yes/no, 3 for yes/no/maybe).
   The scorers use A-D for every model. For Llama, 55 (NF4) and 80 (bf16) replies named a letter that does not exist for the item, such as "C" on a
   yes/no question. They are (almost all) stored as unparsed but scored as wrong answers. Accuracy is identical either way; only the parse-failure count differs.
9. **Sampling noise:** a single run per model at temperature 0.1, with no repeated seeds. The CIs cover item sampling, not decoding randomness.
