# V8 Current Output Contract

Original date: 2026-07-10

Updated: 2026-07-12

Status: ETF-only V8 development contract. Phase 2 and the D+1/D+5/D+8 technical tests are complete; Beta has been dropped. Technical validation passed, but the primary D+1 directional evidence does not support activation.

## Defaults and Active Trigger

```text
DEFAULT_COUNT_X = 5
DEFAULT_SCORE_Y = 75.0
CONFIRMED_ENTRY_MIN_SCORE = 85
```

ETF post-processing is eligible only when:

```text
Final_Decision == MOMENTUM_ACTIVE
AND
Score >= CONFIRMED_ENTRY_MIN_SCORE
```

`--score-y` and `--count-x` control only final-summary presentation. They do not participate in the ETF trigger.

## Score Contract

Published `Score` remains constrained to `0..100`.

| Final decision | Maximum published Score |
|---|---:|
| `MOMENTUM_ACTIVE` | 100 |
| `MOMENTUM_PRESENT_WAIT_CONFIRMATION` | 84 |
| `REJECT` | 49 |

The ETF post-processor cannot modify `Score`, component scores, decisions, or ranks. Beta is not calculated and cannot modify any output.

## Score_Message Contract

For an eligible Active row, `Score_Message` contains ETF context only.

Mapped example:

```text
Active momentum confirmed. Verified top-10 ETF mappings: SMH 19.20%; VGT 16.77%; FTEC 16.60%.
```

No verified mapping:

```text
Active momentum confirmed. No USA-listed ETF mapping could be conservatively verified as a top-ten holding.
```

Failure example:

```text
Active momentum confirmed. ETF mapping is unavailable (<reason>); Score is unchanged.
```

WAIT and REJECT rows do not call the ETF source and retain a blank `Score_Message`.

## ETF Eligibility and Ordering

A mapping is displayed only when all conditions pass:

- ETF ticker exists in the local US ETF master.
- ETF is not identified as leveraged or inverse.
- Stock holding weight is strictly greater than `100/11` percent, conservatively proving top-ten membership.

At most three mappings are displayed, sorted by:

```text
Holding_Weight_Pct DESC
ETF_Ticker ASC
```

Lower-weight exposures are omitted because the reverse source does not publish holding rank. No percentage is fabricated.

## Network, Cache, and Failure Contract

- One stock-specific TradingView funds-page request is permitted per uncached Active stock.
- Successful results are cached by stock code for 24 hours by default.
- No per-ETF holdings request exists in `Momentum_Detector_V8.py` or `ETF_Context_V8.py` production lookup.
- No ETF-universe Yahoo/yfinance scan is allowed.
- Timeout, HTTP error, empty response, or schema change fails open into `Score_Message`.
- Provider response hash, retrieval time, latency, URL, and filter counts are available in the mapping context/audit result.

## Append-Only Execution Log

Default path:

```text
D:/Tools/Stock_MomentumDetector/Processed_Data/V8_Momentum_Execution_Log.csv
```

Every processed ticker is appended before final-summary filtering. A reader may inspect completed rows while the scan continues when it uses non-exclusive file access.

## Final Summary

Default path:

```text
D:/Tools/Stock_MomentumDetector/Processed_Data/V8_Momentum_Execution_Dump.csv
```

It is written after the scan and contains the sorted top `--count-x` rows satisfying `Score >= --score-y`.

## Feature State

Implemented in development:

- Semantic Active-only ETF trigger.
- Direct stock-specific ETF exposure lookup.
- Local US ETF whitelist.
- Conservative top-ten proof and leverage exclusion.
- Top-three sorting.
- Persistent TTL cache and bounded timeout.
- ETF-only `Score_Message` rules.
- Fail-open Score invariance.
- Five-stock API/data-quality validation runner.

Dropped:

- Beta calculation.
- Beta messaging.
- Any Beta influence on Score or action context.

V8 remains non-operational pending broader backtest execution, review of the unfavorable 10-stock sample, and explicit user signoff supported by expanded evidence.

Canonical validation evidence:

```text
backtests/V8_ETF_Phase2/runs/V8ETF_20260711T135316Z_6fa10c6
docs/V8_ETF_PHASE2_CONCLUSION_2026-07-11.md
```

Comprehensive backtest specification:

```text
docs/V8_COMPREHENSIVE_BACKTEST_PLAN_2026-07-12.md
```

The existing ETF validation proves sample mapping quality and production-path behavior. It does not establish broad historical momentum performance. Historical ETF outcome claims require point-in-time mapping and holdings evidence; otherwise the combined stock-and-ETF outcome study is prospective.

Completed 10-stock technical evidence:

```text
backtests/V8_Comprehensive/runs/V8FULL_20260711T192053Z_ffe1567_20260712
docs/V8_COMPREHENSIVE_BACKTEST_CONCLUSION_2026-07-12.md
```

The execution did not change this output contract. Score invariance passed on all 620 replayed rows. The same-quarter ETF analysis is assumption-limited and the momentum results do not support V8 operational activation.

Directional validation evidence:

```text
backtests/V8_Directional_Persistence/runs/V8DIR_20260711T193832Z_0568444
docs/V8_DIRECTIONAL_PERSISTENCE_CONCLUSION_2026-07-12.md
```

The directional test does not change `Score`, decisions, ETF triggering, or output fields. It defines the research gate as D+1 Close above D Close, with D+5 and D+8 used as persistence references.
