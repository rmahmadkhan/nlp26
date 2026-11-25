# Scores for gpt-6-luna (answers re-parsed from raw replies, parser v2)

| script | cond | n | accuracy | source-weighted acc* | parse fail | zs non-compliant (not a bare letter) | mean in tok | mean out tok (visible+thinking) |
|---|---|---|---|---|---|---|---|---|
| en | umcot | 366 | 82.2 | 82.2 | 0 (0.0%) | - | 151 | 4 |
| en | zs | 366 | 81.7 | 81.7 | 0 (0.0%) | 0 (0.0%) | 124 | 4 |
| ru | umcot | 366 | 80.1 | 80.1 | 0 (0.0%) | - | 176 | 4 |
| ru | zs | 366 | 79.5 | 79.5 | 0 (0.0%) | 0 (0.0%) | 149 | 4 |
| ur | umcot | 366 | 74.9 | 74.9 | 0 (0.0%) | - | 159 | 4 |
| ur | zs | 366 | 74.9 | 74.9 | 0 (0.0%) | 0 (0.0%) | 132 | 4 |

*re-weighted to the subset source mix (over sources with >=10 items done), to offset processing-order imbalance.

## Paired comparisons (items answered in both; diff = first - second, pp)

| cond | pair | n paired | acc 1st | acc 2nd | diff | 95% bootstrap CI (10k) | b01/b10 | McNemar exact p |
|---|---|---|---|---|---|---|---|---|
| umcot | EN-UR | 366 | 82.2 | 74.9 | +7.4 | [+3.6, +11.2] | 38/11 | 0.000142 |
| umcot | EN-RU | 366 | 82.2 | 80.1 | +2.2 | [-1.1, +5.5] | 23/15 | 0.256 |
| umcot | RU-UR | 366 | 80.1 | 74.9 | +5.2 | [+1.4, +9.3] | 37/18 | 0.0145 |
| zs | EN-UR | 366 | 81.7 | 74.9 | +6.8 | [+3.0, +10.9] | 40/15 | 0.00102 |
| zs | EN-RU | 366 | 81.7 | 79.5 | +2.2 | [-1.1, +5.5] | 24/16 | 0.268 |
| zs | RU-UR | 366 | 79.5 | 74.9 | +4.6 | [+0.5, +8.7] | 38/21 | 0.0363 |

## Accuracy by source dataset (%; n in brackets)

| script/cond | bioasq | medmcqa | medqa | mmlu | pubmedqa |
|---|---|---|---|---|---|
| en/umcot | 87.5 [32] | 79.3 [208] | 86.5 [52] | 95.9 [49] | 64.0 [25] |
| en/zs | 84.4 [32] | 79.3 [208] | 84.6 [52] | 95.9 [49] | 64.0 [25] |
| ru/umcot | 81.2 [32] | 77.4 [208] | 86.5 [52] | 89.8 [49] | 68.0 [25] |
| ru/zs | 81.2 [32] | 75.5 [208] | 86.5 [52] | 91.8 [49] | 72.0 [25] |
| ur/umcot | 84.4 [32] | 73.6 [208] | 63.5 [52] | 87.8 [49] | 72.0 [25] |
| ur/zs | 87.5 [32] | 74.0 [208] | 59.6 [52] | 87.8 [49] | 72.0 [25] |

## Reply script for reasoning outputs (heuristic: Arabic-script share; Roman Urdu vs English by function words)

| asked | n | replied en | replied ru | replied ur | % in asked script |
|---|---|---|---|---|---|
| en/umcot | 366 | 366 | 0 | 0 | 100% |
| ru/umcot | 366 | 366 | 0 | 0 | 0% |
| ur/umcot | 366 | 366 | 0 | 0 | 0% |
