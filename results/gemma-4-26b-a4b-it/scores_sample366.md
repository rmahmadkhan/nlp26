# Scores for gemma-4-26b-a4b-it (answers re-parsed from raw replies, parser v2)

| script | cond | n | accuracy | source-weighted acc* | parse fail | zs non-compliant (not a bare letter) | mean in tok | mean out tok (visible+thinking) |
|---|---|---|---|---|---|---|---|---|
| en | umcot | 366 | 80.6 | 80.6 | 0 (0.0%) | - | 152 | 370 |
| en | zs | 366 | 77.6 | 77.6 | 1 (0.3%) | 2 (0.5%) | 121 | 2 |
| ru | umcot | 366 | 69.9 | 69.9 | 3 (0.8%) | - | 173 | 205 |
| ru | zs | 366 | 68.0 | 68.0 | 2 (0.5%) | 3 (0.8%) | 142 | 2 |
| ur | umcot | 366 | 63.9 | 63.9 | 0 (0.0%) | - | 156 | 232 |
| ur | zs | 366 | 53.3 | 53.3 | 1 (0.3%) | 2 (0.5%) | 125 | 2 |

*re-weighted to the subset source mix (over sources with >=10 items done), to offset processing-order imbalance.

## Paired comparisons (items answered in both; diff = first - second, pp)

| cond | pair | n paired | acc 1st | acc 2nd | diff | 95% bootstrap CI (10k) | b01/b10 | McNemar exact p |
|---|---|---|---|---|---|---|---|---|
| umcot | EN-UR | 366 | 80.6 | 63.9 | +16.7 | [+11.5, +22.1] | 84/23 | 2.4e-09 |
| umcot | EN-RU | 366 | 80.6 | 69.9 | +10.7 | [+6.0, +15.3] | 62/23 | 2.77e-05 |
| umcot | RU-UR | 366 | 69.9 | 63.9 | +6.0 | [+1.4, +10.9] | 52/30 | 0.0198 |
| zs | EN-UR | 366 | 77.6 | 53.3 | +24.3 | [+18.8, +29.8] | 110/21 | 9.43e-16 |
| zs | EN-RU | 366 | 77.6 | 68.0 | +9.6 | [+4.6, +14.2] | 59/24 | 0.000155 |
| zs | RU-UR | 366 | 68.0 | 53.3 | +14.8 | [+9.6, +20.2] | 79/25 | 1.05e-07 |

## Accuracy by source dataset (%; n in brackets)

| script/cond | bioasq | medmcqa | medqa | mmlu | pubmedqa |
|---|---|---|---|---|---|
| en/umcot | 81.2 [32] | 76.4 [208] | 90.4 [52] | 95.9 [49] | 64.0 [25] |
| en/zs | 78.1 [32] | 71.6 [208] | 90.4 [52] | 95.9 [49] | 64.0 [25] |
| ru/umcot | 75.0 [32] | 61.5 [208] | 86.5 [52] | 83.7 [49] | 72.0 [25] |
| ru/zs | 78.1 [32] | 61.1 [208] | 80.8 [52] | 83.7 [49] | 56.0 [25] |
| ur/umcot | 71.9 [32] | 61.5 [208] | 55.8 [52] | 77.6 [49] | 64.0 [25] |
| ur/zs | 68.8 [32] | 50.5 [208] | 38.5 [52] | 71.4 [49] | 52.0 [25] |

## Reply script for reasoning outputs (heuristic: Arabic-script share; Roman Urdu vs English by function words)

| asked | n | replied en | replied ru | replied ur | % in asked script |
|---|---|---|---|---|---|
| en/umcot | 366 | 366 | 0 | 0 | 100% |
| ru/umcot | 366 | 364 | 0 | 0 | 0% |
| ur/umcot | 366 | 366 | 0 | 0 | 0% |
