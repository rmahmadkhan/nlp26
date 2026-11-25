# Notebooks

Both notebooks contain all of their code as readable cells, copied verbatim from `scripts/`, so the prompts and the parser are identical
to the command-line scripts. Every code cell has a short "Step N" note above it saying what it does, what it reads and what it writes.
They load only data from `DATA_DIR`: a folder with `share/nlp_project_sample366.jsonl`, `data/`, and (for score-only) `results/` and
`expected_results.json`. Ways to provide it:
(a) in Colab, upload `nlp_project_data.zip` (or the whole replication package zip) when asked, or drop it in the Colab **Files** tab
and run `!unzip -q /content/nlp_project_data.zip -d /content` (gives `/content/nlp_project_data`, which is found automatically);
(b) unzip it on Google Drive and set `DATA_DIR`, e.g. `/content/drive/MyDrive/nlp_project_data`;
(c) set a local path, or run from the package root or from `notebooks/` (auto-detected).

- `nlp_project_api_models.ipynb`: default `MODE = 'score_only'` regenerates every table for all six models from the included raw
  outputs and asserts they match `expected_results.json` (no keys, no API calls, about 10 s). `MODE = 'run'` re-runs GPT-6 Luna,
  Gemma 4 26B-A4B and Gemini 3.5 Flash-Lite with our exact settings into `<DATA_DIR>/results_rerun/` (resumable; `SMOKE_ITEMS` for a
  tiny test). Keys come from Colab secrets or the environment variables `OPENAI_API_KEY` / `GEMINI_API_KEY`.
- `nlp_project_small_models.ipynb`: GPU runtime. Runs Qwen3.5 0.8B (NF4), Llama 3.2 1B Instruct (NF4) and Llama 3.2 1B Instruct
  (bf16, or fp16 on GPUs without bf16) into `<DATA_DIR>/results_rerun/<tag>/`, then scores them. It needs the `HF_TOKEN` Colab secret and
  the Llama 3.2 licence accepted on Hugging Face. Resumable. Qwen thinking is disabled (`enable_thinking=False`). Sampling: temperature 0.1,
  top_p 1.0, top_k 0, repetition_penalty 1.0, max 2,048 new tokens, seed 42 + batch offset.

## executed/ (kept with outputs for review)
- `executed/nlp_project_small_models_executed.ipynb`: our actual small-model run on Colab (NVIDIA L4, 2026-11-24), with all outputs.
  Its code cells and outputs are unchanged; only the "Step N" markdown notes were inserted. This run wrote to `results/<tag>/` (the
  current notebook writes new runs to `results_rerun/` so the included results are never touched); those outputs are the
  `results/qwen3.5-0.8b-bnb4`, `results/llama3.2-1b-instruct-bnb4` and `results/llama3.2-1b-instruct-bf16` folders in this package.
  No token appears in it (the token was read from a Colab secret).
- `executed/nlp_project_api_models_score_only_executed.ipynb`: the API notebook run headless in `score_only` mode from the package
  root (`jupyter nbconvert --execute`), ending in PASS. The local folder path in its output was replaced by `/path/to/...`.

Note: the executed small-models notebook shows the code as it was when it ran. Since then, `score_extra.py` gained one extra table in the
combined summaries ("Paper rows vs our successors"). Prompts, parser, runner and every number are unchanged, and the per-model score files it
produced are byte-identical to the ones regenerated from `scripts/`.
