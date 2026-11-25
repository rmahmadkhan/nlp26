# Scores for llama3.2-1b-instruct-bf16 (answers re-parsed from raw replies, parser v2)

| script | cond | n | accuracy | source-weighted acc* | parse fail | zs non-compliant (not a bare letter) | mean in tok | mean out tok (visible+thinking) |
|---|---|---|---|---|---|---|---|---|
| en | umcot | 366 | 25.7 | 25.7 | 42 (11.5%) | - | 183 | 2 |
| en | zs | 366 | 38.3 | 38.3 | 0 (0.0%) | 64 (17.5%) | 155 | 3 |
| ru | umcot | 366 | 30.6 | 30.6 | 20 (5.5%) | - | 214 | 22 |
| ru | zs | 366 | 28.7 | 28.7 | 1 (0.3%) | 40 (10.9%) | 186 | 3 |
| ur | umcot | 366 | 18.3 | 18.3 | 32 (8.7%) | - | 241 | 11 |
| ur | zs | 366 | 21.0 | 21.0 | 7 (1.9%) | 7 (1.9%) | 213 | 2 |

*re-weighted to the subset source mix (over sources with >=10 items done), to offset processing-order imbalance.

## Paired comparisons (items answered in both; diff = first - second, pp)

| cond | pair | n paired | acc 1st | acc 2nd | diff | 95% bootstrap CI (10k) | b01/b10 | McNemar exact p |
|---|---|---|---|---|---|---|---|---|
| umcot | EN-UR | 366 | 25.7 | 18.3 | +7.4 | [+0.8, +13.7] | 85/58 | 0.0293 |
| umcot | EN-RU | 366 | 25.7 | 30.6 | -4.9 | [-11.7, +2.2] | 76/94 | 0.192 |
| umcot | RU-UR | 366 | 30.6 | 18.3 | +12.3 | [+6.8, +18.0] | 80/35 | 3.28e-05 |
| zs | EN-UR | 366 | 38.3 | 21.0 | +17.2 | [+10.7, +23.5] | 111/48 | 6.35e-07 |
| zs | EN-RU | 366 | 38.3 | 28.7 | +9.6 | [+4.1, +14.8] | 69/34 | 0.000728 |
| zs | RU-UR | 366 | 28.7 | 21.0 | +7.7 | [+2.2, +13.1] | 67/39 | 0.00842 |

## Accuracy by source dataset (%; n in brackets)

| script/cond | bioasq | medmcqa | medqa | mmlu | pubmedqa |
|---|---|---|---|---|---|
| en/umcot | 12.5 [32] | 24.5 [208] | 30.8 [52] | 32.7 [49] | 28.0 [25] |
| en/zs | 59.4 [32] | 31.7 [208] | 32.7 [52] | 46.9 [49] | 60.0 [25] |
| ru/umcot | 59.4 [32] | 25.5 [208] | 25.0 [52] | 28.6 [49] | 52.0 [25] |
| ru/zs | 62.5 [32] | 24.0 [208] | 25.0 [52] | 34.7 [49] | 20.0 [25] |
| ur/umcot | 6.2 [32] | 17.8 [208] | 17.3 [52] | 26.5 [49] | 24.0 [25] |
| ur/zs | 28.1 [32] | 20.7 [208] | 15.4 [52] | 20.4 [49] | 28.0 [25] |

## Reply script for reasoning outputs (heuristic: Arabic-script share; Roman Urdu vs English by function words)

| asked | n | replied en | replied ru | replied ur | % in asked script |
|---|---|---|---|---|---|
| en/umcot | 366 | 366 | 0 | 0 | 100% |
| ru/umcot | 366 | 231 | 135 | 0 | 37% |
| ur/umcot | 366 | 297 | 0 | 68 | 19% |
