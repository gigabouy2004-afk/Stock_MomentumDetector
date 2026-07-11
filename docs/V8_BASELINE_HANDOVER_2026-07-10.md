# V8 Development Handover

Original date: 2026-07-10

Updated: 2026-07-12

Status: ETF Phase 2 implementation and five-stock validation complete. Comprehensive momentum-and-ETF backtesting is planned but not executed; V8 remains development-only.

## Baseline

V8 was forked from corrected V7 commit:

```text
9a4b0ba Fix V7 score range and append-only execution log
```

Intentional V8 differences:

```text
Engine identity: V8
Default top count: 5
Default final-summary threshold: 75
Execution log: Processed_Data/V8_Momentum_Execution_Log.csv
Final summary: Processed_Data/V8_Momentum_Execution_Dump.csv
Run ID prefix: V8_
Post-processing: ETF information only
```

## Inherited Correctness Rules

- Score remains within `0..100`.
- REJECT remains capped at `49`, independently of `--score-y`.
- CLI filters affect only the final summary.
- Every processed ticker reaches the append-only execution log before filtering.
- V7 remains untouched and operational.

## Beta Retirement

The Beta pilot was completed and preserved for audit, but its relationship with forward price performance was not sufficiently conclusive for production use. On 2026-07-11 the user closed and dropped the Beta track.

Consequences:

- No active V8 import of `Beta_Context_V8.py`.
- No Beta calculation or message in the production scan.
- No further Beta backtesting or signoff work.
- Frozen historical Beta artifacts remain immutable evidence only.

## ETF Phase 2 Implementation

Active files:

```text
Momentum_Detector_V8.py
ETF_Context_V8.py
Backtest_Momentum_Detector_V8_ETF.py
config/V8_Post_Processor_Message_Map.csv
tests/test_etf_context_v8.py
```

Trigger:

```text
Final_Decision == MOMENTUM_ACTIVE
AND Score >= CONFIRMED_ENTRY_MIN_SCORE
```

The ETF processor writes only `Score_Message` and never changes `Score`.

The live lookup makes one stock-specific request, filters against the local US ETF master, excludes leveraged/inverse funds, applies the strict `weight > 100/11` top-ten proof, returns at most three mappings, caches successes, and fails open.

The separate backtest may call returned ETFs' holdings pages solely to validate rank. That validation path is not imported by the production engine.

## Remaining Transition Gate

Before V8 becomes operational:

1. Review and approve the comprehensive backtest design.
2. Implement the deterministic replay runner, independent validator, and required tests.
3. Execute development, validation, final-test, ticker-holdout, matched WAIT, V7 comparison, and robustness stages.
4. Expand ETF functional validation and use point-in-time historical mappings or a prospective shadow cohort for combined outcomes.
5. Review the completed backtest conclusion, sample ETF messages, and all documented data limitations.
6. Record explicit V8 operational signoff.

Canonical evidence:

```text
backtests/V8_ETF_Phase2/runs/V8ETF_20260711T135316Z_6fa10c6
docs/V8_ETF_PHASE2_CONCLUSION_2026-07-11.md
```

Comprehensive execution specification:

```text
docs/V8_COMPREHENSIVE_BACKTEST_PLAN_2026-07-12.md
```

Important boundary:

- The existing five-stock ETF run is a production-path and mapping-quality validation, not a comprehensive V8 momentum backtest.
- The retired Beta pilot is historical audit evidence and is not part of the active V8 test scope.
- Current ETF mappings cannot be assigned to historical signals without dated point-in-time holdings evidence.
- No comprehensive V8 run ID exists yet.

Until signoff:

```text
V7 = operational baseline
V8 = development only; comprehensive backtest pending
```
