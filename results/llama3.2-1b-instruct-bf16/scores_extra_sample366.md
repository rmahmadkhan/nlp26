# Extra scores for Llama 3.2 1B Instruct (bf16) (llama3.2-1b-instruct-bf16), parser v2

| script | cond | n | accuracy | 95% bootstrap CI | parse fail | zs not bare letter | hit max_tokens |
|---|---|---|---|---|---|---|---|
| en | zs | 366 | 0.38 | [0.33, 0.43] | 0 (0.0%) | 64 (17.5%) | 0 (0.0%) |
| en | umcot | 366 | 0.26 | [0.21, 0.30] | 1 (0.3%) | - | 0 (0.0%) |
| ru | zs | 366 | 0.29 | [0.24, 0.33] | 0 (0.0%) | 40 (10.9%) | 0 (0.0%) |
| ru | umcot | 366 | 0.31 | [0.26, 0.35] | 18 (4.9%) | - | 2 (0.5%) |
| ur | zs | 366 | 0.21 | [0.17, 0.25] | 0 (0.0%) | 7 (1.9%) | 0 (0.0%) |
| ur | umcot | 366 | 0.18 | [0.14, 0.22] | 4 (1.1%) | - | 1 (0.3%) |

## Paired gaps (accuracy in %, diff = first - second in percentage points; bootstrap 10k; exact McNemar)

| cond | pair | n | acc 1st | acc 2nd | diff | 95% CI | b01/b10 | p |
|---|---|---|---|---|---|---|---|---|
| zs | EN-RU | 366 | 38.25 | 28.69 | +9.56 | [+4.10, +14.75] | 69/34 | 0.000728 |
| zs | EN-UR | 366 | 38.25 | 21.04 | +17.21 | [+10.66, +23.50] | 111/48 | 6.35e-07 |
| zs | RU-UR | 366 | 28.69 | 21.04 | +7.65 | [+2.19, +13.11] | 67/39 | 0.00842 |
| umcot | EN-RU | 366 | 25.68 | 30.60 | -4.92 | [-11.75, +2.19] | 76/94 | 0.192 |
| umcot | EN-UR | 366 | 25.68 | 18.31 | +7.38 | [+0.82, +13.66] | 85/58 | 0.0293 |
| umcot | RU-UR | 366 | 30.60 | 18.31 | +12.30 | [+6.83, +18.03] | 80/35 | 3.28e-05 |

## Urdu: questions truncated in the released U-MIRAGE CSV vs complete (original questions used)

| cond | subset | n | UR acc | EN acc (same items) | EN-UR | 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|
| zs | truncated | 70 | 17.14 | 35.71 | +18.57 | [+4.29, +32.86] | 0.0192 |
| zs | complete | 296 | 21.96 | 38.85 | +16.89 | [+9.80, +24.32] | 1.61e-05 |
| umcot | truncated | 70 | 18.57 | 34.29 | +15.71 | [+0.00, +31.43] | 0.0895 |
| umcot | complete | 296 | 18.24 | 23.65 | +5.41 | [-1.35, +12.16] | 0.149 |
