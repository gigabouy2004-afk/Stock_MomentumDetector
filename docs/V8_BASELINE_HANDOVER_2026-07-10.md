# V8 Development Baseline Handover

Date: 2026-07-10

Status: Beta Release-1 development implementation created; not operational.

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

Core score calculation, decision rules, live-price handling, and append-log/final-summary separation otherwise match the corrected V7 baseline at fork time. Beta is isolated in a post-processing module and does not feed back into those calculations.

## Inherited Correctness Rules

- Published scores remain within `0..100`.
- REJECT is capped at `49`, independent of `--score-y`.
- `--score-y` filters only the final summary.
- Every processed ticker is appended to the full execution log before summary filtering.
- The execution log is readable during a scan when the reader uses non-exclusive read access.
- Final summary generation remains an end-of-run operation.
- Post-processor eligibility is based on `MOMENTUM_ACTIVE` plus the programmed `CONFIRMED_ENTRY_MIN_SCORE`, never on CLI summary filters.

## Development Status

V8 now contains the development Beta post-processor, a traceable historical replay runner, a read-only offline random-sample validator, message-map configuration, and unit tests. The ETF post-processor is not implemented.

The canonical first pilot and preliminary findings are recorded in:

```text
docs/V8_BETA_RELEASE1_PILOT_2026-07-10.md
```

Required work before operational signoff:

1. Complete the broader chronological Beta development/validation/holdout study.
2. Complete all planned offline random-validation rounds.
3. Review Beta/industry/market linkage and approve the Beta message rules.
4. Direct ETF reverse-lookup API selection and validation.
5. ETF mapping implementation and latency/data-quality validation.
6. Combined V8 regression and live checks.
7. Explicit user operational signoff.

Current Beta implementation contract:

```text
Trigger = Final_Decision == MOMENTUM_ACTIVE
          AND Score >= CONFIRMED_ENTRY_MIN_SCORE
Current programmed threshold = 85
CLI --score-y / --count-x participation = none
Core Score modification = none
Beta output = Score_Message only
```

Until those gates pass:

```text
V7 = operational baseline
V8 = development only
```
