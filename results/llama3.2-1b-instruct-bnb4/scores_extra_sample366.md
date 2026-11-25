# Extra scores for Llama 3.2 1B Instruct (q, NF4) (llama3.2-1b-instruct-bnb4), parser v2

| script | cond | n | accuracy | 95% bootstrap CI | parse fail | zs not bare letter | hit max_tokens |
|---|---|---|---|---|---|---|---|
| en | zs | 366 | 0.36 | [0.31, 0.40] | 0 (0.0%) | 32 (8.7%) | 0 (0.0%) |
| en | umcot | 366 | 0.33 | [0.28, 0.38] | 0 (0.0%) | - | 0 (0.0%) |
| ru | zs | 366 | 0.36 | [0.31, 0.41] | 0 (0.0%) | 33 (9.0%) | 0 (0.0%) |
| ru | umcot | 366 | 0.31 | [0.27, 0.36] | 2 (0.5%) | - | 1 (0.3%) |
| ur | zs | 366 | 0.26 | [0.22, 0.31] | 0 (0.0%) | 68 (18.6%) | 0 (0.0%) |
| ur | umcot | 366 | 0.23 | [0.19, 0.28] | 0 (0.0%) | - | 0 (0.0%) |

## Paired gaps (accuracy in %, diff = first - second in percentage points; bootstrap 10k; exact McNemar)

| cond | pair | n | acc 1st | acc 2nd | diff | 95% CI | b01/b10 | p |
|---|---|---|---|---|---|---|---|---|
| zs | EN-RU | 366 | 35.52 | 36.07 | -0.55 | [-5.19, +4.10] | 37/39 | 0.909 |
| zs | EN-UR | 366 | 35.52 | 26.23 | +9.29 | [+3.01, +15.30] | 86/52 | 0.00479 |
| zs | RU-UR | 366 | 36.07 | 26.23 | +9.84 | [+3.55, +16.12] | 87/51 | 0.00275 |
| umcot | EN-RU | 366 | 33.06 | 31.42 | +1.64 | [-2.19, +5.74] | 31/25 | 0.504 |
| umcot | EN-UR | 366 | 33.06 | 23.50 | +9.56 | [+4.37, +14.75] | 65/30 | 0.000425 |
| umcot | RU-UR | 366 | 31.42 | 23.50 | +7.92 | [+2.73, +13.11] | 63/34 | 0.00423 |

## Urdu: questions truncated in the released U-MIRAGE CSV vs complete (original questions used)

| cond | subset | n | UR acc | EN acc (same items) | EN-UR | 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|
| zs | truncated | 70 | 20.00 | 24.29 | +4.29 | [-7.14, +15.71] | 0.629 |
| zs | complete | 296 | 27.70 | 38.18 | +10.47 | [+3.38, +17.91] | 0.00615 |
| umcot | truncated | 70 | 32.86 | 31.43 | -1.43 | [-12.86, +10.00] | 1 |
| umcot | complete | 296 | 21.28 | 33.45 | +12.16 | [+6.42, +17.91] | 5.57e-05 |
