# Extra scores for Qwen3.5 0.8B (q, NF4) (qwen3.5-0.8b-bnb4), parser v2

| script | cond | n | accuracy | 95% bootstrap CI | parse fail | zs not bare letter | hit max_tokens |
|---|---|---|---|---|---|---|---|
| en | zs | 366 | 0.40 | [0.35, 0.45] | 0 (0.0%) | 1 (0.3%) | 0 (0.0%) |
| en | umcot | 366 | 0.36 | [0.31, 0.41] | 0 (0.0%) | - | 0 (0.0%) |
| ru | zs | 366 | 0.33 | [0.28, 0.38] | 0 (0.0%) | 1 (0.3%) | 0 (0.0%) |
| ru | umcot | 366 | 0.27 | [0.22, 0.32] | 78 (21.3%) | - | 20 (5.5%) |
| ur | zs | 366 | 0.33 | [0.28, 0.38] | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| ur | umcot | 366 | 0.33 | [0.28, 0.38] | 1 (0.3%) | - | 2 (0.5%) |

## Paired gaps (accuracy in %, diff = first - second in percentage points; bootstrap 10k; exact McNemar)

| cond | pair | n | acc 1st | acc 2nd | diff | 95% CI | b01/b10 | p |
|---|---|---|---|---|---|---|---|---|
| zs | EN-RU | 366 | 40.16 | 33.33 | +6.83 | [+2.19, +11.48] | 49/24 | 0.00463 |
| zs | EN-UR | 366 | 40.16 | 32.79 | +7.38 | [+1.91, +12.84] | 68/41 | 0.0124 |
| zs | RU-UR | 366 | 33.33 | 32.79 | +0.55 | [-4.64, +5.74] | 47/45 | 0.917 |
| umcot | EN-RU | 366 | 36.07 | 27.05 | +9.02 | [+2.73, +15.03] | 82/49 | 0.00498 |
| umcot | EN-UR | 366 | 36.07 | 32.79 | +3.28 | [-1.64, +8.20] | 49/37 | 0.235 |
| umcot | RU-UR | 366 | 27.05 | 32.79 | -5.74 | [-11.20, +0.00] | 48/69 | 0.064 |

## Urdu: questions truncated in the released U-MIRAGE CSV vs complete (original questions used)

| cond | subset | n | UR acc | EN acc (same items) | EN-UR | 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|
| zs | truncated | 70 | 24.29 | 32.86 | +8.57 | [-5.71, +22.86] | 0.327 |
| zs | complete | 296 | 34.80 | 41.89 | +7.09 | [+1.01, +13.18] | 0.0275 |
| umcot | truncated | 70 | 31.43 | 38.57 | +7.14 | [-4.29, +18.57] | 0.359 |
| umcot | complete | 296 | 33.11 | 35.47 | +2.36 | [-3.04, +7.77] | 0.464 |
