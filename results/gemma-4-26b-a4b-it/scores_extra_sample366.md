# Extra scores for Gemma 4 26B-A4B (gemma-4-26b-a4b-it), parser v2

| script | cond | n | accuracy | 95% bootstrap CI | parse fail | zs not bare letter | hit max_tokens |
|---|---|---|---|---|---|---|---|
| en | zs | 366 | 0.78 | [0.73, 0.82] | 1 (0.3%) | 2 (0.5%) | 0 (0.0%) |
| en | umcot | 366 | 0.81 | [0.76, 0.85] | 0 (0.0%) | - | 2 (0.5%) |
| ru | zs | 366 | 0.68 | [0.63, 0.73] | 2 (0.5%) | 3 (0.8%) | 0 (0.0%) |
| ru | umcot | 366 | 0.70 | [0.65, 0.75] | 3 (0.8%) | - | 4 (1.1%) |
| ur | zs | 366 | 0.53 | [0.48, 0.58] | 1 (0.3%) | 2 (0.5%) | 0 (0.0%) |
| ur | umcot | 366 | 0.64 | [0.59, 0.69] | 0 (0.0%) | - | 0 (0.0%) |

## Paired gaps (accuracy in %, diff = first - second in percentage points; bootstrap 10k; exact McNemar)

| cond | pair | n | acc 1st | acc 2nd | diff | 95% CI | b01/b10 | p |
|---|---|---|---|---|---|---|---|---|
| zs | EN-RU | 366 | 77.60 | 68.03 | +9.56 | [+4.64, +14.21] | 59/24 | 0.000155 |
| zs | EN-UR | 366 | 77.60 | 53.28 | +24.32 | [+18.85, +29.78] | 110/21 | 9.43e-16 |
| zs | RU-UR | 366 | 68.03 | 53.28 | +14.75 | [+9.56, +20.22] | 79/25 | 1.05e-07 |
| umcot | EN-RU | 366 | 80.60 | 69.95 | +10.66 | [+6.01, +15.30] | 62/23 | 2.77e-05 |
| umcot | EN-UR | 366 | 80.60 | 63.93 | +16.67 | [+11.48, +22.13] | 84/23 | 2.4e-09 |
| umcot | RU-UR | 366 | 69.95 | 63.93 | +6.01 | [+1.37, +10.93] | 52/30 | 0.0198 |

## Urdu: questions truncated in the released U-MIRAGE CSV vs complete (original questions used)

| cond | subset | n | UR acc | EN acc (same items) | EN-UR | 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|
| zs | truncated | 70 | 44.29 | 90.00 | +45.71 | [+34.29, +57.14] | 4.07e-09 |
| zs | complete | 296 | 55.41 | 74.66 | +19.26 | [+13.18, +25.68] | 4.59e-09 |
| umcot | truncated | 70 | 60.00 | 88.57 | +28.57 | [+17.14, +40.00] | 1.1e-05 |
| umcot | complete | 296 | 64.86 | 78.72 | +13.85 | [+7.77, +19.93] | 9.81e-06 |
