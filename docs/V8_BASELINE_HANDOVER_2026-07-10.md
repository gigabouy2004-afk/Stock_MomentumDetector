# V8 Development Baseline Handover

Date: 2026-07-10

Status: Development baseline created; not operational.

## Source

V8 was forked from the V7 score/logging correction committed as:

```text
9a4b0ba Fix V7 score range and append-only execution log
```

Baseline engine:

```text
Momentum_Detector_V8.py
```

## Intentional Differences From Corrected V7

```text
Engine identity: V8
Default top count: 5
Default final-summary threshold: 75
Execution log: Processed_Data/V8_Momentum_Execution_Log.csv
Final summary: Processed_Data/V8_Momentum_Execution_Dump.csv
Run ID prefix: V8_
```

Core score calculation, decision rules, live-price handling, and the new append-log/final-summary separation otherwise match the corrected V7 baseline at fork time.

## Inherited Correctness Rules

- Published scores remain within `0..100`.
- REJECT is capped at `49`, independent of `--score-y`.
- `--score-y` filters only the final summary.
- Every processed ticker is appended to the full execution log before summary filtering.
- The execution log is readable during a scan when the reader uses non-exclusive read access.
- Final summary generation remains an end-of-run operation.
- Post-processor eligibility is based on `MOMENTUM_ACTIVE` plus the programmed `CONFIRMED_ENTRY_MIN_SCORE`, never on CLI summary filters.

## Development Status

V8 does not yet contain the planned Beta or ETF post-processors.

Required work before operational signoff:

1. Beta calculation implementation.
2. Traceable historical backtesting and offline random validation.
3. Beta message-rule review and signoff.
4. Direct ETF reverse-lookup API selection and validation.
5. ETF mapping implementation and latency/data-quality validation.
6. Combined V8 regression and live checks.
7. Explicit user operational signoff.

Until those gates pass:

```text
V7 = operational baseline
V8 = development only
```
