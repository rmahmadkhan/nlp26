# API models on the 366-item sample (parser v2)

## Paper-style accuracy table (fraction correct, 2 decimals; n per cell in the per-model files)

| Model | EN Zero-Shot | EN CoT | RU Zero-Shot | RU CoT | UR Zero-Shot | UR CoT |
|---|---|---|---|---|---|---|
| GPT-6 Luna | 0.82 | 0.82 | 0.80 | 0.80 | 0.75 | 0.75 |
| Gemma 4 26B-A4B | 0.78 | 0.81 | 0.68 | 0.70 | 0.53 | 0.64 |
| Gemini 3.5 Flash-Lite | 0.83 | 0.84 | 0.78 | 0.80 | 0.69 | 0.77 |
| *U-MIRAGE paper reference rows (full benchmark, 7,663 items):* | | | | | | |
| GPT-5 nano [paper] | 0.80 | 0.79 | 0.75 | 0.75 | 0.73 | 0.70 |
| Gemini 2.0 Flash-Lite [paper] | 0.72 | 0.78 | 0.66 | 0.74 | 0.68 | 0.70 |
| Gemma 2 2B [paper] | 0.42 | 0.43 | 0.32 | 0.35 | 0.31 | 0.34 |

## Accuracy in % (2 decimals)

| Model | EN ZS | EN CoT | RU ZS | RU CoT | UR ZS | UR CoT |
|---|---|---|---|---|---|---|
| GPT-6 Luna | 81.69 | 82.24 | 79.51 | 80.05 | 74.86 | 74.86 |
| Gemma 4 26B-A4B | 77.60 | 80.60 | 68.03 | 69.95 | 53.28 | 63.93 |
| Gemini 3.5 Flash-Lite | 82.79 | 84.15 | 78.42 | 79.78 | 69.13 | 77.05 |

## Paper rows vs our successors (accuracy in %, 2 decimals; each paper row directly above its successor)

Paper = U-MIRAGE, full benchmark (7,663 items). Ours = a random 366-item sample (seed 42), so the rows are not item-matched. Gemma 4 26B-A4B is not size-matched to Gemma 2 2B (26B total / ~4B active parameters vs 2B).

| Model | EN ZS | EN CoT | RU ZS | RU CoT | UR ZS | UR CoT |
|---|---|---|---|---|---|---|
| GPT-5 nano [paper] | 79.62 | 78.65 | 75.02 | 74.98 | 72.99 | 70.23 |
| GPT-6 Luna [ours] | 81.69 | 82.24 | 79.51 | 80.05 | 74.86 | 74.86 |
| Gemini 2.0 Flash-Lite [paper] | 71.77 | 77.79 | 65.82 | 74.14 | 67.68 | 70.13 |
| Gemini 3.5 Flash-Lite [ours] | 82.79 | 84.15 | 78.42 | 79.78 | 69.13 | 77.05 |
| Gemma 2 2B [paper] | 41.98 | 43.25 | 32.47 | 35.00 | 31.24 | 33.67 |
| Gemma 4 26B-A4B [ours] | 77.60 | 80.60 | 68.03 | 69.95 | 53.28 | 63.93 |

## Paired gaps (accuracy %, diff in pp)

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

## Truncated vs complete Urdu questions (accuracy %, diff in pp)

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

## Compliance

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
