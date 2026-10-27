# Bicycle speed analysis pass

All speeds remain estimates using the existing learned camera calibration. No scale was fitted to study means. Sensitivity bounds use assumed errors; they are not verified accuracy intervals. Prior HiPerGator coverage/people may differ; it is context, not a paired comparison.

| Location | Usable / annotated | Study reference mph | Prior HiPerGator mph | Old manual mph | Endpoint mph | Robust mph | Sensitivity range mph |
|---|---:|---:|---:|---:|---:|---:|---|
| Aloma | 4/4 | 13.58 | Unavailable | 19.81 | 17.36 | 19.43 | 16.73–22.04 |
| Carroll | 2/2 | 11.89 | Unavailable | 12.37 | 12.19 | 12.59 | 10.84–14.28 |
| Colonial | 3/3 | 9.54 | 7.63 | 10.71 | 10.64 | 10.77 | 9.39–12.24 |
| Columbia | 4/4 | 12.24 | 3.04 | 12.47 | 12.34 | 12.62 | 10.92–14.30 |
| Edgewater | 5/6 | 12.02 | 17.57 | 14.00 | 8.54 | 11.51 | 9.89–13.02 |
| Lee | 4/4 | 8.73 | 9.88 | 12.36 | 12.31 | 12.40 | 10.74–14.08 |
| Pleasant Hill | 2/2 | 9.86 | 8.99 | 8.99 | 8.51 | 8.80 | 7.66–9.97 |
| Rinehart/CST | 1/1 | 12.92 | Unavailable | 12.01 | 11.89 | 12.48 | 10.92–14.15 |
| University | 4/4 | 9.49 | 11.17 | 16.98 | 16.97 | 17.11 | 14.86–19.50 |

Assumptions: click noise SD 3 pixels; uniform camera scale ±15%; 500 simulations. These are illustrative engineering choices, not measured error bounds. Site ranges average all usable cyclists in each simulation with shared camera scale. They omit unknown geometric distortion, identity errors and sampling uncertainty.

The three manual estimators use identical points/times and calibration for each usable encounter. Robust fitting reduces sensitivity to some outliers but does not guarantee better accuracy. Endpoint speed can underestimate curved travel. Rejected encounters stay in cyclists.csv with reasons.

Timestamp audit: 18/18 review clips audited. This checks the re-encoded review clips, not the original hourly recordings; it cannot rule out timing problems introduced earlier in extraction.

cyclists.csv contains exact saved recording times (filename-inferred clocks), statuses, flags and per-cyclist estimates. plots/ shows each accepted trajectory and fitted distance over time. timestamp_audit.json and timestamps/ retain packet PTS evidence. Browser annotation seconds remain unchanged; packet index is not assumed to equal decoded frame index. No extra half-speed factor is applied.

[Robust slope reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.theilslopes.html). This is a project-specific estimator, not a paper reproduction.
