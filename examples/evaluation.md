Evaluation on synthetic data, seed=42, weeks=4.

| Incident type | static | zscore | ewma | seasonal_1w | seasonal_2w | burn_rate | seasonal_2w+burn_rate |
|---|---|---|---|---|---|---|---|
| traffic_drop (n=3) | 0/3 | 3/3 in 2m | 3/3 in 2m | 3/3 in 4m | 3/3 in 4m | 0/3 | 3/3 in 4m |
| error_spike (n=3) | 3/3 in 2m | 3/3 in 2m | 3/3 in 2m | 3/3 in 4m | 3/3 in 4m | 3/3 in 13m | 3/3 in 4m |
| latency_regression (n=3) | 0/3 | 3/3 in 2m | 3/3 in 2m | 3/3 in 4m | 3/3 in 4m | 1/3 in 57m | 3/3 in 4m |
| slow_burn (n=3) | 0/3 | 0/3 | 0/3 | 3/3 in 5.1h | 3/3 in 5.1h | 3/3 in 10.2h | 3/3 in 5.1h |
| **Recall** | 25% | 75% | 75% | 100% | 100% | 58% | 100% |
| **Precision** | 25% | 52% | 41% | 54% | 58% | 70% | 61% |
| **False alerts / week** | 2.2 | 2.8 | 3.2 | 3.2 | 2.8 | 0.8 | 3.5 |
