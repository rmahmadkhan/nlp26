# Scores for llama3.2-1b-instruct-bnb4 (answers re-parsed from raw replies, parser v2)

| script | cond | n | accuracy | source-weighted acc* | parse fail | zs non-compliant (not a bare letter) | mean in tok | mean out tok (visible+thinking) |
|---|---|---|---|---|---|---|---|---|
| en | umcot | 366 | 33.1 | 33.1 | 2 (0.5%) | - | 183 | 3 |
| en | zs | 366 | 35.5 | 35.5 | 0 (0.0%) | 32 (8.7%) | 155 | 2 |
| ru | umcot | 366 | 31.4 | 31.4 | 11 (3.0%) | - | 214 | 11 |
| ru | zs | 366 | 36.1 | 36.1 | 0 (0.0%) | 33 (9.0%) | 186 | 2 |
| ur | umcot | 366 | 23.5 | 23.5 | 41 (11.2%) | - | 241 | 6 |
| ur | zs | 366 | 26.2 | 26.2 | 3 (0.8%) | 68 (18.6%) | 213 | 4 |

*re-weighted to the subset source mix (over sources with >=10 items done), to offset processing-order imbalance.

## Paired comparisons (items answered in both; diff = first - second, pp)

| cond | pair | n paired | acc 1st | acc 2nd | diff | 95% bootstrap CI (10k) | b01/b10 | McNemar exact p |
|---|---|---|---|---|---|---|---|---|
| umcot | EN-UR | 366 | 33.1 | 23.5 | +9.6 | [+4.4, +14.8] | 65/30 | 0.000425 |
| umcot | EN-RU | 366 | 33.1 | 31.4 | +1.6 | [-2.2, +5.7] | 31/25 | 0.504 |
| umcot | RU-UR | 366 | 31.4 | 23.5 | +7.9 | [+2.7, +13.1] | 63/34 | 0.00423 |
| zs | EN-UR | 366 | 35.5 | 26.2 | +9.3 | [+3.0, +15.3] | 86/52 | 0.00479 |
| zs | EN-RU | 366 | 35.5 | 36.1 | -0.5 | [-5.2, +4.1] | 37/39 | 0.909 |
| zs | RU-UR | 366 | 36.1 | 26.2 | +9.8 | [+3.6, +16.1] | 87/51 | 0.00275 |

## Accuracy by source dataset (%; n in brackets)

| script/cond | bioasq | medmcqa | medqa | mmlu | pubmedqa |
|---|---|---|---|---|---|
| en/umcot | 53.1 [32] | 26.9 [208] | 28.8 [52] | 34.7 [49] | 64.0 [25] |
| en/zs | 56.2 [32] | 31.2 [208] | 21.2 [52] | 40.8 [49] | 64.0 [25] |
| ru/umcot | 43.8 [32] | 28.4 [208] | 19.2 [52] | 36.7 [49] | 56.0 [25] |
| ru/zs | 62.5 [32] | 30.8 [208] | 26.9 [52] | 36.7 [49] | 64.0 [25] |
| ur/umcot | 0.0 [32] | 22.1 [208] | 25.0 [52] | 36.7 [49] | 36.0 [25] |
| ur/zs | 37.5 [32] | 26.0 [208] | 15.4 [52] | 26.5 [49] | 36.0 [25] |

## Reply script for reasoning outputs (heuristic: Arabic-script share; Roman Urdu vs English by function words)

| asked | n | replied en | replied ru | replied ur | % in asked script |
|---|---|---|---|---|---|
| en/umcot | 366 | 366 | 0 | 0 | 100% |
| ru/umcot | 366 | 321 | 45 | 0 | 12% |
| ur/umcot | 366 | 262 | 0 | 104 | 28% |
