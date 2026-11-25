# Scores for gemini-3.5-flash-lite (answers re-parsed from raw replies, parser v2)

| script | cond | n | accuracy | source-weighted acc* | parse fail | zs non-compliant (not a bare letter) | mean in tok | mean out tok (visible+thinking) |
|---|---|---|---|---|---|---|---|---|
| en | umcot | 366 | 84.2 | 84.2 | 0 (0.0%) | - | 152 | 255 |
| en | zs | 366 | 82.8 | 82.8 | 2 (0.5%) | 157 (42.9%) | 121 | 101 |
| ru | umcot | 366 | 79.8 | 79.8 | 0 (0.0%) | - | 173 | 240 |
| ru | zs | 366 | 78.4 | 78.4 | 0 (0.0%) | 15 (4.1%) | 142 | 9 |
| ur | umcot | 366 | 77.0 | 77.0 | 0 (0.0%) | - | 156 | 224 |
| ur | zs | 366 | 69.1 | 69.1 | 2 (0.5%) | 27 (7.4%) | 125 | 13 |

*re-weighted to the subset source mix (over sources with >=10 items done), to offset processing-order imbalance.

## Paired comparisons (items answered in both; diff = first - second, pp)

| cond | pair | n paired | acc 1st | acc 2nd | diff | 95% bootstrap CI (10k) | b01/b10 | McNemar exact p |
|---|---|---|---|---|---|---|---|---|
| umcot | EN-UR | 366 | 84.2 | 77.0 | +7.1 | [+3.3, +10.9] | 38/12 | 0.000306 |
| umcot | EN-RU | 366 | 84.2 | 79.8 | +4.4 | [+1.1, +7.7] | 26/10 | 0.0113 |
| umcot | RU-UR | 366 | 79.8 | 77.0 | +2.7 | [-0.8, +6.3] | 29/19 | 0.193 |
| zs | EN-UR | 366 | 82.8 | 69.1 | +13.7 | [+9.0, +18.3] | 65/15 | 1.41e-08 |
| zs | EN-RU | 366 | 82.8 | 78.4 | +4.4 | [+0.5, +8.2] | 35/19 | 0.0402 |
| zs | RU-UR | 366 | 78.4 | 69.1 | +9.3 | [+4.9, +13.7] | 53/19 | 7.56e-05 |

## Accuracy by source dataset (%; n in brackets)

| script/cond | bioasq | medmcqa | medqa | mmlu | pubmedqa |
|---|---|---|---|---|---|
| en/umcot | 84.4 [32] | 81.2 [208] | 96.2 [52] | 95.9 [49] | 60.0 [25] |
| en/zs | 81.2 [32] | 79.3 [208] | 96.2 [52] | 95.9 [49] | 60.0 [25] |
| ru/umcot | 84.4 [32] | 76.4 [208] | 94.2 [52] | 87.8 [49] | 56.0 [25] |
| ru/zs | 87.5 [32] | 73.1 [208] | 90.4 [52] | 85.7 [49] | 72.0 [25] |
| ur/umcot | 78.1 [32] | 76.9 [208] | 71.2 [52] | 87.8 [49] | 68.0 [25] |
| ur/zs | 81.2 [32] | 69.2 [208] | 55.8 [52] | 79.6 [49] | 60.0 [25] |

## Reply script for reasoning outputs (heuristic: Arabic-script share; Roman Urdu vs English by function words)

| asked | n | replied en | replied ru | replied ur | % in asked script |
|---|---|---|---|---|---|
| en/umcot | 366 | 366 | 0 | 0 | 100% |
| ru/umcot | 366 | 310 | 56 | 0 | 15% |
| ur/umcot | 366 | 282 | 0 | 84 | 23% |
