# V8 Foundation Validation Handover

Date: 2026-07-12

Status: Mainline V8 now enforces EMA200 plus configurable MACD `8/21/5` before Setup/Momentum. Focused 20-stock/four-date validation passed. V7 remains the operational baseline until broader validation and explicit signoff.

## Start Here

Read in this order:

1. `docs/V8_FOUNDATION_VALIDATION_CONCLUSION_2026-07-12.md`
2. `docs/V8_CURRENT_OUTPUT_CONTRACT_2026-07-10.md`
3. `docs/V8_DEVELOPMENT_CHARTER_2026-07-10.md`
4. `docs/V1_V8_EMA200_MACD_FOUNDATION_DISCOVERY_2026-07-12.md`
5. `docs/V8_COMPREHENSIVE_BACKTEST_PLAN_2026-07-12.md`

## Mainline Behavior

Entry point:

```text
Momentum_Detector_V8.py
```

Defaults:

```text
MACD fast/slow/signal = 8/21/5
Foundation policy = enforce
Foundation valid = Close > EMA200 AND MACD line > signal AND MACD line > 0
Active threshold = 85
ETF = informational postprocessor only for Active
```

CLI controls:

```text
--macd-fast
--macd-slow
--macd-signal
--foundation-policy enforce|audit
```

`audit` is a regression facility, not the normal operating policy.

New output fields:

```text
Foundation_Status
Foundation_Qualified
Foundation_Reason
Foundation_Policy
```

An existing append-only V8 log with the old header is preserved; V8 opens a timestamped log using the new schema.

## Files Added or Changed

Implementation and shared replay:

```text
Momentum_Detector_V8.py
Backtest_Momentum_Detector_V8.py
```

Focused runner and independent validator:

```text
Backtest_Momentum_Detector_V8_Foundation.py
Validate_Momentum_Detector_V8_Foundation.py
config/V8_Foundation_Validation_Config.json
tests/test_v8_foundation_backtest.py
tests/test_v8_macd.py
```

Canonical frozen run:

```text
backtests/V8_Foundation_Validation/runs/V8FOUND_20260712T182945Z_cf0c908
```

## Result Snapshot

```text
Stocks / dates / rows: 20 / 4 / 80
Foundation Valid: 25
MACD Reset: 28
Below EMA200: 27
Active / Wait / Reject: 5 / 30 / 45
Active D+1: 4/5 positive
Active D+5: 5/5 positive
Active D+8: 4/5 positive
Regression failures: 0
Independent recompute failures: 0
ETF mappings returned / Q2 accepted: 21 / 7
ETF score mutations: 0
Checksum validation: PASS
Focused tests: 22 PASS
```

## Important Interpretation

Foundation Valid materially improved D+1 behavior: 76% positive with +2.21% mean, compared with 53.6% and -0.05% for MACD Reset. This supports the first filter for the user's primary directional objective.

The reset cohort remained strong at D+5/D+8. Five legacy Active rows were blocked by the new MACD rule; only 2/5 were positive at D+1, but 4/5 were positive at D+8. Preserve `FOUNDATION_TREND_VALID_MACD_RESET` as a WAIT state for the joint analysis rather than treating it as a failed trend.

The full scorer remains restrictive after Foundation qualification: 18 Foundation Valid rows were still rejected. Those rows were positive 13/18 at D+1, 16/18 at D+5, and 14/18 at D+8. This suggests the next review should examine downstream Setup/Momentum thresholds independently from the restored Foundation rule.

## Reproduction

Run focused tests:

```powershell
python -m unittest tests.test_v8_macd tests.test_v8_comprehensive_backtest tests.test_v8_directional_persistence tests.test_v8_foundation_backtest tests.test_etf_context_v8
```

Run the frozen-scope workflow again with new provider data:

```powershell
python Backtest_Momentum_Detector_V8_Foundation.py --config config/V8_Foundation_Validation_Config.json --output-root backtests/V8_Foundation_Validation/runs
```

Validate the sealed canonical run, including checksums:

```powershell
python Validate_Momentum_Detector_V8_Foundation.py backtests/V8_Foundation_Validation/runs/V8FOUND_20260712T182945Z_cf0c908
```

## Remaining Gates

- Joint review of the Foundation Valid, MACD Reset, and Foundation-Valid-but-rejected cohorts.
- Multi-regime chronological validation beyond 2026Q2.
- Untouched date and ticker holdouts.
- Industrial-sector expansion using the same frozen contract.
- Historical hourly/live-quote evidence or explicit acceptance of daily-only replay.
- Prospective ETF shadow evidence with more Active rows.
- Explicit user approval before V8 replaces V7.

Current boundary:

```text
V7 = OPERATIONAL BASELINE
V8 = FOUNDATION IMPLEMENTED AND FOCUSED VALIDATION PASSED; DEVELOPMENT ONLY
```
