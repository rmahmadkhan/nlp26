# Scores for qwen3.5-0.8b-bnb4 (answers re-parsed from raw replies, parser v2)

| script | cond | n | accuracy | source-weighted acc* | parse fail | zs non-compliant (not a bare letter) | mean in tok | mean out tok (visible+thinking) |
|---|---|---|---|---|---|---|---|---|
| en | umcot | 366 | 36.1 | 36.1 | 0 (0.0%) | - | 162 | 3 |
| en | zs | 366 | 40.2 | 40.2 | 0 (0.0%) | 1 (0.3%) | 134 | 3 |
| ru | umcot | 366 | 27.0 | 27.0 | 78 (21.3%) | - | 191 | 277 |
| ru | zs | 366 | 33.3 | 33.3 | 0 (0.0%) | 1 (0.3%) | 163 | 2 |
| ur | umcot | 366 | 32.8 | 32.8 | 1 (0.3%) | - | 181 | 21 |
| ur | zs | 366 | 32.8 | 32.8 | 0 (0.0%) | 0 (0.0%) | 153 | 2 |

*re-weighted to the subset source mix (over sources with >=10 items done), to offset processing-order imbalance.

## Paired comparisons (items answered in both; diff = first - second, pp)

| cond | pair | n paired | acc 1st | acc 2nd | diff | 95% bootstrap CI (10k) | b01/b10 | McNemar exact p |
|---|---|---|---|---|---|---|---|---|
| umcot | EN-UR | 366 | 36.1 | 32.8 | +3.3 | [-1.6, +8.2] | 49/37 | 0.235 |
| umcot | EN-RU | 366 | 36.1 | 27.0 | +9.0 | [+2.7, +15.0] | 82/49 | 0.00498 |
| umcot | RU-UR | 366 | 27.0 | 32.8 | -5.7 | [-11.2, +0.0] | 48/69 | 0.064 |
| zs | EN-UR | 366 | 40.2 | 32.8 | +7.4 | [+1.9, +12.8] | 68/41 | 0.0124 |
| zs | EN-RU | 366 | 40.2 | 33.3 | +6.8 | [+2.2, +11.5] | 49/24 | 0.00463 |
| zs | RU-UR | 366 | 33.3 | 32.8 | +0.5 | [-4.6, +5.7] | 47/45 | 0.917 |

## Accuracy by source dataset (%; n in brackets)

| script/cond | bioasq | medmcqa | medqa | mmlu | pubmedqa |
|---|---|---|---|---|---|
| en/umcot | 40.6 [32] | 33.7 [208] | 34.6 [52] | 49.0 [49] | 28.0 [25] |
| en/zs | 56.2 [32] | 36.1 [208] | 32.7 [52] | 40.8 [49] | 68.0 [25] |
| ru/umcot | 46.9 [32] | 22.1 [208] | 26.9 [52] | 36.7 [49] | 24.0 [25] |
| ru/zs | 53.1 [32] | 29.8 [208] | 25.0 [52] | 32.7 [49] | 56.0 [25] |
| ur/umcot | 62.5 [32] | 28.8 [208] | 26.9 [52] | 36.7 [49] | 32.0 [25] |
| ur/zs | 56.2 [32] | 28.8 [208] | 25.0 [52] | 26.5 [49] | 64.0 [25] |

## Reply script for reasoning outputs (heuristic: Arabic-script share; Roman Urdu vs English by function words)

| asked | n | replied en | replied ru | replied ur | % in asked script |
|---|---|---|---|---|---|
| en/umcot | 366 | 366 | 0 | 0 | 100% |
| ru/umcot | 366 | 352 | 14 | 0 | 4% |
| ur/umcot | 366 | 366 | 0 | 0 | 0% |
