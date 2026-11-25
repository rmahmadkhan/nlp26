# Extra scores for Gemini 3.5 Flash-Lite (gemini-3.5-flash-lite), parser v2

| script | cond | n | accuracy | 95% bootstrap CI | parse fail | zs not bare letter | hit max_tokens |
|---|---|---|---|---|---|---|---|
| en | zs | 366 | 0.83 | [0.79, 0.87] | 2 (0.5%) | 157 (42.9%) | 0 (0.0%) |
| en | umcot | 366 | 0.84 | [0.80, 0.88] | 0 (0.0%) | - | 0 (0.0%) |
| ru | zs | 366 | 0.78 | [0.74, 0.83] | 0 (0.0%) | 15 (4.1%) | 0 (0.0%) |
| ru | umcot | 366 | 0.80 | [0.76, 0.84] | 0 (0.0%) | - | 0 (0.0%) |
| ur | zs | 366 | 0.69 | [0.64, 0.74] | 2 (0.5%) | 27 (7.4%) | 0 (0.0%) |
| ur | umcot | 366 | 0.77 | [0.73, 0.81] | 0 (0.0%) | - | 0 (0.0%) |

## Paired gaps (accuracy in %, diff = first - second in percentage points; bootstrap 10k; exact McNemar)

| cond | pair | n | acc 1st | acc 2nd | diff | 95% CI | b01/b10 | p |
|---|---|---|---|---|---|---|---|---|
| zs | EN-RU | 366 | 82.79 | 78.42 | +4.37 | [+0.55, +8.20] | 35/19 | 0.0402 |
| zs | EN-UR | 366 | 82.79 | 69.13 | +13.66 | [+9.02, +18.31] | 65/15 | 1.41e-08 |
| zs | RU-UR | 366 | 78.42 | 69.13 | +9.29 | [+4.92, +13.66] | 53/19 | 7.56e-05 |
| umcot | EN-RU | 366 | 84.15 | 79.78 | +4.37 | [+1.09, +7.65] | 26/10 | 0.0113 |
| umcot | EN-UR | 366 | 84.15 | 77.05 | +7.10 | [+3.28, +10.93] | 38/12 | 0.000306 |
| umcot | RU-UR | 366 | 79.78 | 77.05 | +2.73 | [-0.82, +6.28] | 29/19 | 0.193 |

## Urdu: questions truncated in the released U-MIRAGE CSV vs complete (original questions used)

| cond | subset | n | UR acc | EN acc (same items) | EN-UR | 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|
| zs | truncated | 70 | 57.14 | 92.86 | +35.71 | [+24.29, +47.14] | 5.96e-08 |
| zs | complete | 296 | 71.96 | 80.41 | +8.45 | [+3.72, +13.18] | 0.00102 |
| umcot | truncated | 70 | 71.43 | 92.86 | +21.43 | [+12.86, +31.43] | 6.1e-05 |
| umcot | complete | 296 | 78.38 | 82.09 | +3.72 | [-0.34, +7.77] | 0.0895 |
