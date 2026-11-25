# Small-model successors on the 366-item sample (parser v2)

## Paper-style accuracy table (fraction correct, 2 decimals; n per cell in the per-model files)

| Model | EN Zero-Shot | EN CoT | RU Zero-Shot | RU CoT | UR Zero-Shot | UR CoT |
|---|---|---|---|---|---|---|
| Qwen3.5 0.8B (q, NF4) | 0.40 | 0.36 | 0.33 | 0.27 | 0.33 | 0.33 |
| Llama 3.2 1B Instruct (q, NF4) | 0.36 | 0.33 | 0.36 | 0.31 | 0.26 | 0.23 |
| Llama 3.2 1B Instruct (bf16) | 0.38 | 0.26 | 0.29 | 0.31 | 0.21 | 0.18 |
| *U-MIRAGE paper reference rows (full benchmark, 7,663 items):* | | | | | | |
| Qwen 2.5 0.5B (q) [paper] | 0.26 | 0.30 | 0.24 | 0.28 | 0.23 | 0.27 |
| LLaMA 3.2 1B (q) [paper] | 0.19 | 0.39 | 0.20 | 0.24 | 0.19 | 0.18 |
| LLaMA 3.2 1B [paper] | 0.45 | 0.44 | 0.34 | 0.36 | 0.34 | 0.31 |

## Accuracy in % (2 decimals)

| Model | EN ZS | EN CoT | RU ZS | RU CoT | UR ZS | UR CoT |
|---|---|---|---|---|---|---|
| Qwen3.5 0.8B (q, NF4) | 40.16 | 36.07 | 33.33 | 27.05 | 32.79 | 32.79 |
| Llama 3.2 1B Instruct (q, NF4) | 35.52 | 33.06 | 36.07 | 31.42 | 26.23 | 23.50 |
| Llama 3.2 1B Instruct (bf16) | 38.25 | 25.68 | 28.69 | 30.60 | 21.04 | 18.31 |

## Paper rows vs our successors (accuracy in %, 2 decimals; each paper row directly above its successor)

Paper = U-MIRAGE, full benchmark (7,663 items). Ours = a random 366-item sample (seed 42), so the rows are not item-matched. Gemma 4 26B-A4B is not size-matched to Gemma 2 2B (26B total / ~4B active parameters vs 2B).

| Model | EN ZS | EN CoT | RU ZS | RU CoT | UR ZS | UR CoT |
|---|---|---|---|---|---|---|
| Qwen 2.5 0.5B (q) [paper] | 25.92 | 29.74 | 23.78 | 27.65 | 23.05 | 27.21 |
| Qwen3.5 0.8B (q, NF4) [ours] | 40.16 | 36.07 | 33.33 | 27.05 | 32.79 | 32.79 |
| LLaMA 3.2 1B (q) [paper] | 18.86 | 38.89 | 19.82 | 24.00 | 18.83 | 17.81 |
| Llama 3.2 1B Instruct (q, NF4) [ours] | 35.52 | 33.06 | 36.07 | 31.42 | 26.23 | 23.50 |
| LLaMA 3.2 1B [paper] | 45.49 | 44.37 | 34.48 | 36.16 | 33.64 | 31.24 |
| Llama 3.2 1B Instruct (bf16) [ours] | 38.25 | 25.68 | 28.69 | 30.60 | 21.04 | 18.31 |

## Paired gaps (accuracy %, diff in pp)

| model | cond | pair | n | acc 1st | acc 2nd | diff | 95% CI | b01/b10 | McNemar p |
|---|---|---|---|---|---|---|---|---|---|
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

## Truncated vs complete Urdu questions (accuracy %, diff in pp)

| model | cond | subset | n | UR acc | EN acc | EN-UR | 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|---|
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

## Compliance

| model | run | n | parse fail | zs not bare letter | hit max_tokens |
|---|---|---|---|---|---|
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
