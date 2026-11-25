# Aircraft Conflict Detection

A geometric aircraft conflict detector using closest-approach vector math, benchmarked against a time-sweep ground truth on 2,000 generated scenarios.

## Results (E1, 2,000 generated scenarios)

| Method | Converging detection rate | Random false alarm rate | Runtime per pair |
|---|---|---|---|
| v1: closest-approach only | 77.64% (191/246) | 0.00% | 0.006 ms |
| v2: time-sweep (1 s steps) | 100.00% (246/246) | 0.00% | 0.705 ms |

Overall, v1 detected 191 of 247 true conflicts (77.33%). The v2 sweep matches the ground truth by construction, since both use the same logic, so it confirms consistency rather than independent correctness.

The random group contains only 1 true conflict in 1,000 pairs, so its detection rate is not meaningful. It is used only to measure false alarms.

## Limitations

- **Constant velocity:** aircraft are assumed to hold speed and heading. Climbs and turns are not modelled.
- **Flat Earth:** coordinates are treated as a flat plane, reasonable over short distances only.
- **Discrete sweep:** the ground truth and v2 use 1-second steps and can miss very brief conflicts.
- **v1 definition gap:** closest-approach timing can miss a moment when both limits are violated together. This accounts for the 22.36% miss rate.
- **Synthetic scenarios:** traffic is generated randomly, not observed. 

- **Definition gap found and fixed:** the first version checked separation only at the moment of closest 3D approach. It missed conflicts where both limits were violated at a different moment. The window-sweep version (v2) catches these, at about 100x the runtime.
