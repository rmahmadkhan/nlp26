# Extra scores for GPT-6 Luna (gpt-6-luna), parser v2

| script | cond | n | accuracy | 95% bootstrap CI | parse fail | zs not bare letter | hit max_tokens |
|---|---|---|---|---|---|---|---|
| en | zs | 366 | 0.82 | [0.78, 0.86] | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| en | umcot | 366 | 0.82 | [0.78, 0.86] | 0 (0.0%) | - | 0 (0.0%) |
| ru | zs | 366 | 0.80 | [0.75, 0.84] | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| ru | umcot | 366 | 0.80 | [0.76, 0.84] | 0 (0.0%) | - | 0 (0.0%) |
| ur | zs | 366 | 0.75 | [0.70, 0.79] | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| ur | umcot | 366 | 0.75 | [0.70, 0.79] | 0 (0.0%) | - | 0 (0.0%) |

## Paired gaps (accuracy in %, diff = first - second in percentage points; bootstrap 10k; exact McNemar)

| cond | pair | n | acc 1st | acc 2nd | diff | 95% CI | b01/b10 | p |
|---|---|---|---|---|---|---|---|---|
| zs | EN-RU | 366 | 81.69 | 79.51 | +2.19 | [-1.09, +5.46] | 24/16 | 0.268 |
| zs | EN-UR | 366 | 81.69 | 74.86 | +6.83 | [+3.01, +10.93] | 40/15 | 0.00102 |
| zs | RU-UR | 366 | 79.51 | 74.86 | +4.64 | [+0.55, +8.74] | 38/21 | 0.0363 |
| umcot | EN-RU | 366 | 82.24 | 80.05 | +2.19 | [-1.09, +5.46] | 23/15 | 0.256 |
| umcot | EN-UR | 366 | 82.24 | 74.86 | +7.38 | [+3.55, +11.20] | 38/11 | 0.000142 |
| umcot | RU-UR | 366 | 80.05 | 74.86 | +5.19 | [+1.37, +9.29] | 37/18 | 0.0145 |

## Urdu: questions truncated in the released U-MIRAGE CSV vs complete (original questions used)

| cond | subset | n | UR acc | EN acc (same items) | EN-UR | 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|
| zs | truncated | 70 | 64.29 | 85.71 | +21.43 | [+12.86, +31.43] | 6.1e-05 |
| zs | complete | 296 | 77.36 | 80.74 | +3.38 | [-0.68, +7.43] | 0.154 |
| umcot | truncated | 70 | 67.14 | 87.14 | +20.00 | [+8.57, +31.43] | 0.00131 |
| umcot | complete | 296 | 76.69 | 81.08 | +4.39 | [+0.68, +8.11] | 0.0294 |
