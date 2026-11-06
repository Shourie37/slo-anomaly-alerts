# Incident summary: checkout-api

| Group | Opened (UTC) | Duration | Highest severity | Route | Alerts |
|---|---|---|---|---|---|
| G1 | 2026-01-12T03:09:00Z | 102m | ticket | ticket | 1 |
| G2 | 2026-01-12T14:12:00Z | 15m | ticket | ticket | 1 |
| G3 | 2026-01-12T19:04:00Z | 15m | ticket | ticket | 1 |
| G4 | 2026-01-13T21:05:00Z | 29m | page | pager | 2 |
| G5 | 2026-01-14T09:05:00Z | 49m | ticket | ticket | 1 |
| G6 | 2026-01-15T10:15:00Z | 39m | ticket | ticket | 1 |
| G7 | 2026-01-15T11:55:00Z | 15m | ticket | ticket | 1 |
| G8 | 2026-01-15T17:15:00Z | 72m | ticket | ticket | 1 |
| G9 | 2026-01-17T15:31:00Z | 102m | ticket | ticket | 1 |
| G10 | 2026-01-18T13:10:00Z | 15m | ticket | ticket | 1 |
| G11 | 2026-01-19T12:18:00Z | 15.6h | page | pager | 2 |
| G12 | 2026-01-21T09:13:00Z | 35m | ticket | ticket | 2 |
| G13 | 2026-01-21T13:18:00Z | 102m | page | pager | 2 |
| G14 | 2026-01-22T14:44:00Z | 30m | ticket | ticket | 1 |
| G15 | 2026-01-23T04:08:00Z | 15m | ticket | ticket | 1 |
| G16 | 2026-01-23T05:17:00Z | 29m | ticket | ticket | 1 |
| G17 | 2026-01-23T05:59:00Z | 16.1h | page | pager | 2 |
| G18 | 2026-01-24T08:58:00Z | 6.3h | page | pager | 2 |
| G19 | 2026-01-25T09:50:00Z | 48m | ticket | ticket | 2 |
| G20 | 2026-01-25T13:25:00Z | 2.6h | ticket | ticket | 2 |
| G21 | 2026-01-26T21:13:00Z | 29m | page | pager | 2 |
| G22 | 2026-01-28T02:51:00Z | 72m | ticket | ticket | 1 |
| G23 | 2026-01-30T14:30:00Z | 72m | ticket | ticket | 1 |
| G24 | 2026-01-31T11:58:00Z | 15m | ticket | ticket | 1 |
| G25 | 2026-02-01T00:12:00Z | 43m | ticket | ticket | 1 |
| G26 | 2026-02-01T01:30:00Z | 15.4h | page | pager | 2 |

## G1: checkout-api

- Opened: 2026-01-12T03:09:00Z
- Resolved: 2026-01-12T04:51:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A1 | seasonal_2w | p99_ms | ticket | 2026-01-12T03:09:00Z | 102m | 901.8 | 210.3 | no |

Timeline:

- 2026-01-12T03:09:00Z `open` -> ticket: checkout-api: p99_ms 845.5 vs expected 200.1 (1w band 200.1..200.1 +/-30%)
- 2026-01-12T04:51:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G2: checkout-api

- Opened: 2026-01-12T14:12:00Z
- Resolved: 2026-01-12T14:27:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A2 | seasonal_2w | error_rate | ticket | 2026-01-12T14:12:00Z | 15m | 0.05078 | 0 | no |

Timeline:

- 2026-01-12T14:12:00Z `open` -> ticket: checkout-api: error_rate 0.05078 vs expected 0 (1w band 0..0 +/-30%)
- 2026-01-12T14:27:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G3: checkout-api

- Opened: 2026-01-12T19:04:00Z
- Resolved: 2026-01-12T19:19:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A3 | seasonal_2w | error_rate | ticket | 2026-01-12T19:04:00Z | 15m | 0.06097 | 0 | no |

Timeline:

- 2026-01-12T19:04:00Z `open` -> ticket: checkout-api: error_rate 0.06097 vs expected 0 (1w band 0..0 +/-30%)
- 2026-01-12T19:19:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G4: checkout-api

- Opened: 2026-01-13T21:05:00Z
- Resolved: 2026-01-13T21:34:00Z
- Notified: yes, page

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A4 | seasonal_2w | error_rate | ticket | 2026-01-13T21:05:00Z | 27m | 0.0858 | 0 | no |
| A5 | burn_rate | availability | page | 2026-01-13T21:14:00Z | 20m | 18.42 | 14.4 | no |

Timeline:

- 2026-01-13T21:05:00Z `open` -> ticket: checkout-api: error_rate 0.0772 vs expected 0 (1w band 0..0 +/-30%)
- 2026-01-13T21:14:00Z `update` -> log: joined: availability SLO 99.90%: burn 17.0x over 1h and 77.9x over 5m >= 14.4x
- 2026-01-13T21:14:00Z `escalate` -> pager: checkout-api: availability SLO 99.90%: burn 17.0x over 1h and 77.9x over 5m >= 14.4x (+1 related)
- 2026-01-13T21:34:00Z `resolve` -> pager: all 2 alert(s) resolved

## G5: checkout-api

- Opened: 2026-01-14T09:05:00Z
- Resolved: 2026-01-14T09:54:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A6 | seasonal_2w | requests | ticket | 2026-01-14T09:05:00Z | 49m | 1783 | 1236 | no |

Timeline:

- 2026-01-14T09:05:00Z `open` -> ticket: checkout-api: requests 1622 vs expected 1174 (1w band 1174..1174 +/-30%)
- 2026-01-14T09:54:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G6: checkout-api

- Opened: 2026-01-15T10:15:00Z
- Resolved: 2026-01-15T10:54:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A7 | seasonal_2w | requests | ticket | 2026-01-15T10:15:00Z | 39m | 1383 | 2060 | no |

Timeline:

- 2026-01-15T10:15:00Z `open` -> ticket: checkout-api: requests 1367 vs expected 1957 (1w band 1957..1957 +/-30%)
- 2026-01-15T10:54:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G7: checkout-api

- Opened: 2026-01-15T11:55:00Z
- Resolved: 2026-01-15T12:10:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A8 | seasonal_2w | error_rate | ticket | 2026-01-15T11:55:00Z | 15m | 0.06021 | 0.0006219 | no |

Timeline:

- 2026-01-15T11:55:00Z `open` -> ticket: checkout-api: error_rate 0.06021 vs expected 0.0006219 (1w band 0.0006219..0.0006219 +/-30%)
- 2026-01-15T12:10:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G8: checkout-api

- Opened: 2026-01-15T17:15:00Z
- Resolved: 2026-01-15T18:27:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A9 | seasonal_2w | requests | ticket | 2026-01-15T17:15:00Z | 72m | 825 | 1775 | no |

Timeline:

- 2026-01-15T17:15:00Z `open` -> ticket: checkout-api: requests 1034 vs expected 1732 (1w band 1732..1732 +/-30%)
- 2026-01-15T18:27:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G9: checkout-api

- Opened: 2026-01-17T15:31:00Z
- Resolved: 2026-01-17T17:13:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A10 | seasonal_2w | p99_ms | ticket | 2026-01-17T15:31:00Z | 102m | 1115 | 246.4 | no |

Timeline:

- 2026-01-17T15:31:00Z `open` -> ticket: checkout-api: p99_ms 996.1 vs expected 247 (1w band 247..247 +/-30%)
- 2026-01-17T17:13:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G10: checkout-api

- Opened: 2026-01-18T13:10:00Z
- Resolved: 2026-01-18T13:25:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A11 | seasonal_2w | error_rate | ticket | 2026-01-18T13:10:00Z | 15m | 0.05227 | 0 | no |

Timeline:

- 2026-01-18T13:10:00Z `open` -> ticket: checkout-api: error_rate 0.05227 vs expected 0 (1w band 0..0 +/-30%)
- 2026-01-18T13:25:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G11: checkout-api

- Opened: 2026-01-19T12:18:00Z
- Resolved: 2026-01-20T03:56:00Z
- Notified: yes, page

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A12 | seasonal_2w | error_rate | ticket | 2026-01-19T12:18:00Z | 9.9h | 0.01542 | 0 | no |
| A13 | burn_rate | availability | page | 2026-01-19T15:10:00Z | 12.8h | 9.69 | 6 | no |

Timeline:

- 2026-01-19T12:18:00Z `open` -> ticket: checkout-api: error_rate 0.005354 vs expected 0 (2w band 0..0 +/-30%)
- 2026-01-19T15:10:00Z `update` -> log: joined: availability SLO 99.90%: burn 1.0x over 3d and 4.9x over 6h >= 1x
- 2026-01-19T16:48:00Z `escalate` -> pager: checkout-api: availability SLO 99.90%: burn 6.0x over 6h and 8.2x over 30m >= 6x (+1 related)
- 2026-01-20T03:56:00Z `resolve` -> pager: all 2 alert(s) resolved _(suppressed: maintenance)_

## G12: checkout-api

- Opened: 2026-01-21T09:13:00Z
- Resolved: 2026-01-21T09:48:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A14 | seasonal_2w | error_rate | ticket | 2026-01-21T09:13:00Z | 15m | 0.05138 | 0 | no |
| A15 | burn_rate | availability | ticket | 2026-01-21T09:13:00Z | 35m | 2.176 | 1 | no |

Timeline:

- 2026-01-21T09:13:00Z `open` -> ticket: checkout-api: error_rate 0.05138 vs expected 0 (2w band 0..0 +/-30%) (+1 related)
- 2026-01-21T09:48:00Z `resolve` -> ticket: all 2 alert(s) resolved

## G13: checkout-api

- Opened: 2026-01-21T13:18:00Z
- Resolved: 2026-01-21T15:00:00Z
- Notified: yes, page

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A16 | seasonal_2w | p99_ms | ticket | 2026-01-21T13:18:00Z | 102m | 1261 | 275.7 | no |
| A17 | burn_rate | latency | page | 2026-01-21T14:11:00Z | 47m | 15.53 | 14.4 | no |

Timeline:

- 2026-01-21T13:18:00Z `open` -> ticket: checkout-api: p99_ms 1088 vs expected 277.2 (2w band 265.9..288.6 +/-30%)
- 2026-01-21T14:11:00Z `update` -> log: joined: latency SLO 99.00%: burn 15.0x over 1h and 15.6x over 5m >= 14.4x
- 2026-01-21T14:11:00Z `escalate` -> pager: checkout-api: latency SLO 99.00%: burn 15.0x over 1h and 15.6x over 5m >= 14.4x (+1 related)
- 2026-01-21T15:00:00Z `resolve` -> pager: all 2 alert(s) resolved

## G14: checkout-api

- Opened: 2026-01-22T14:44:00Z
- Resolved: 2026-01-22T15:14:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A18 | seasonal_2w | requests | ticket | 2026-01-22T14:44:00Z | 30m | 2661 | 1810 | no |

Timeline:

- 2026-01-22T14:44:00Z `open` -> ticket: checkout-api: requests 2645 vs expected 1893 (2w band 1892..1894 +/-30%)
- 2026-01-22T15:14:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G15: checkout-api

- Opened: 2026-01-23T04:08:00Z
- Resolved: 2026-01-23T04:23:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A19 | seasonal_2w | error_rate | ticket | 2026-01-23T04:08:00Z | 15m | 0.005435 | 0 | no |

Timeline:

- 2026-01-23T04:08:00Z `open` -> ticket: checkout-api: error_rate 0.005435 vs expected 0 (2w band 0..0 +/-30%)
- 2026-01-23T04:23:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G16: checkout-api

- Opened: 2026-01-23T05:17:00Z
- Resolved: 2026-01-23T05:46:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A20 | seasonal_2w | error_rate | ticket | 2026-01-23T05:17:00Z | 29m | 0.006547 | 0 | no |

Timeline:

- 2026-01-23T05:17:00Z `open` -> ticket: checkout-api: error_rate 0.005008 vs expected 0 (2w band 0..0 +/-30%)
- 2026-01-23T05:46:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G17: checkout-api

- Opened: 2026-01-23T05:59:00Z
- Resolved: 2026-01-23T22:07:00Z
- Notified: yes, page

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A21 | seasonal_2w | error_rate | ticket | 2026-01-23T05:59:00Z | 10.6h | 0.01377 | 0 | no |
| A22 | burn_rate | availability | page | 2026-01-23T10:29:00Z | 11.6h | 9.917 | 6 | no |

Timeline:

- 2026-01-23T05:59:00Z `open` -> ticket: checkout-api: error_rate 0.006349 vs expected 0 (2w band 0..0 +/-30%)
- 2026-01-23T10:29:00Z `update` -> log: joined: availability SLO 99.90%: burn 6.0x over 6h and 8.1x over 30m >= 6x
- 2026-01-23T10:29:00Z `escalate` -> pager: checkout-api: availability SLO 99.90%: burn 6.0x over 6h and 8.1x over 30m >= 6x (+1 related)
- 2026-01-23T22:07:00Z `resolve` -> pager: all 2 alert(s) resolved

## G18: checkout-api

- Opened: 2026-01-24T08:58:00Z
- Resolved: 2026-01-24T15:18:00Z
- Notified: yes, page

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A23 | seasonal_2w | error_rate | ticket | 2026-01-24T08:58:00Z | 27m | 0.08124 | 0 | no |
| A24 | burn_rate | availability | page | 2026-01-24T08:58:00Z | 6.3h | 20.47 | 14.4 | no |

Timeline:

- 2026-01-24T08:58:00Z `open` -> ticket: checkout-api: error_rate 0.08124 vs expected 0 (2w band 0..0 +/-30%) (+1 related)
- 2026-01-24T09:04:00Z `escalate` -> pager: checkout-api: availability SLO 99.90%: burn 14.7x over 1h and 75.0x over 5m >= 14.4x (+1 related)
- 2026-01-24T15:18:00Z `resolve` -> pager: all 2 alert(s) resolved

## G19: checkout-api

- Opened: 2026-01-25T09:50:00Z
- Resolved: 2026-01-25T10:38:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A25 | seasonal_2w | error_rate | ticket | 2026-01-25T09:50:00Z | 15m | 0.06593 | 0 | no |
| A26 | burn_rate | availability | ticket | 2026-01-25T09:50:00Z | 48m | 2.272 | 1 | no |

Timeline:

- 2026-01-25T09:50:00Z `open` -> ticket: checkout-api: error_rate 0.06593 vs expected 0 (2w band 0..0 +/-30%) (+1 related)
- 2026-01-25T10:38:00Z `resolve` -> ticket: all 2 alert(s) resolved

## G20: checkout-api

- Opened: 2026-01-25T13:25:00Z
- Resolved: 2026-01-25T16:01:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A27 | burn_rate | availability | ticket | 2026-01-25T13:25:00Z | 2.6h | 2.425 | 1 | no |
| A28 | seasonal_2w | error_rate | ticket | 2026-01-25T13:26:00Z | 15m | 0.05534 | 0 | no |

Timeline:

- 2026-01-25T13:25:00Z `open` -> ticket: checkout-api: availability SLO 99.90%: burn 2.4x over 3d and 1.4x over 6h >= 1x
- 2026-01-25T13:26:00Z `update` -> log: joined: error_rate 0.05534 vs expected 0 (2w band 0..0 +/-30%)
- 2026-01-25T16:01:00Z `resolve` -> ticket: all 2 alert(s) resolved

## G21: checkout-api

- Opened: 2026-01-26T21:13:00Z
- Resolved: 2026-01-26T21:42:00Z
- Notified: yes, page

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A29 | seasonal_2w | error_rate | ticket | 2026-01-26T21:13:00Z | 27m | 0.08473 | 0.004136 | no |
| A30 | burn_rate | availability | page | 2026-01-26T21:22:00Z | 20m | 19.23 | 14.4 | no |

Timeline:

- 2026-01-26T21:13:00Z `open` -> ticket: checkout-api: error_rate 0.08473 vs expected 0.004136 (2w band 0..0.008272 +/-30%)
- 2026-01-26T21:22:00Z `update` -> log: joined: availability SLO 99.90%: burn 17.8x over 1h and 76.5x over 5m >= 14.4x
- 2026-01-26T21:22:00Z `escalate` -> pager: checkout-api: availability SLO 99.90%: burn 17.8x over 1h and 76.5x over 5m >= 14.4x (+1 related)
- 2026-01-26T21:42:00Z `resolve` -> pager: all 2 alert(s) resolved

## G22: checkout-api

- Opened: 2026-01-28T02:51:00Z
- Resolved: 2026-01-28T04:03:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A31 | seasonal_2w | requests | ticket | 2026-01-28T02:51:00Z | 72m | 256 | 505.5 | no |

Timeline:

- 2026-01-28T02:51:00Z `open` -> ticket: checkout-api: requests 266 vs expected 480 (2w band 461..499 +/-30%)
- 2026-01-28T04:03:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G23: checkout-api

- Opened: 2026-01-30T14:30:00Z
- Resolved: 2026-01-30T15:42:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A32 | seasonal_2w | requests | ticket | 2026-01-30T14:30:00Z | 72m | 1041 | 1952 | no |

Timeline:

- 2026-01-30T14:30:00Z `open` -> ticket: checkout-api: requests 1066 vs expected 1918 (2w band 1916..1920 +/-30%)
- 2026-01-30T15:42:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G24: checkout-api

- Opened: 2026-01-31T11:58:00Z
- Resolved: 2026-01-31T12:13:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A33 | seasonal_2w | error_rate | ticket | 2026-01-31T11:58:00Z | 15m | 0.05938 | 0 | no |

Timeline:

- 2026-01-31T11:58:00Z `open` -> ticket: checkout-api: error_rate 0.05938 vs expected 0 (2w band 0..0 +/-30%)
- 2026-01-31T12:13:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G25: checkout-api

- Opened: 2026-02-01T00:12:00Z
- Resolved: 2026-02-01T00:55:00Z
- Notified: yes, ticket

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A34 | seasonal_2w | error_rate | ticket | 2026-02-01T00:12:00Z | 43m | 0.008677 | 0 | no |

Timeline:

- 2026-02-01T00:12:00Z `open` -> ticket: checkout-api: error_rate 0.006342 vs expected 0 (2w band 0..0 +/-30%)
- 2026-02-01T00:55:00Z `resolve` -> ticket: all 1 alert(s) resolved

## G26: checkout-api

- Opened: 2026-02-01T01:30:00Z
- Resolved: 2026-02-01T16:52:00Z
- Notified: yes, page

| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |
|---|---|---|---|---|---|---|---|---|
| A35 | seasonal_2w | error_rate | ticket | 2026-02-01T01:30:00Z | 9.8h | 0.01574 | 0 | no |
| A36 | burn_rate | availability | page | 2026-02-01T06:09:00Z | 10.7h | 10.34 | 6 | no |

Timeline:

- 2026-02-01T01:30:00Z `open` -> ticket: checkout-api: error_rate 0.005666 vs expected 0 (2w band 0..0 +/-30%)
- 2026-02-01T06:09:00Z `update` -> log: joined: availability SLO 99.90%: burn 6.0x over 6h and 7.8x over 30m >= 6x
- 2026-02-01T06:09:00Z `escalate` -> pager: checkout-api: availability SLO 99.90%: burn 6.0x over 6h and 7.8x over 30m >= 6x (+1 related)
- 2026-02-01T16:52:00Z `resolve` -> pager: all 2 alert(s) resolved
