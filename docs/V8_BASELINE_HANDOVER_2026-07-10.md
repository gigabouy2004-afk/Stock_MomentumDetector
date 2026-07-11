# V8 Development Handover

Original date: 2026-07-10

Updated: 2026-07-11

Status: ETF Phase 2 development implementation; V8 is not yet operational.

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

1. Complete the canonical five-stock Phase 2 validation.
2. Review latency, rank accuracy, freshness limitations, and sample messages.
3. Confirm no prohibited production network path exists.
4. Record explicit Phase 2 and V8 operational signoff.

Until signoff:

```text
V7 = operational baseline
V8 = development only
```
