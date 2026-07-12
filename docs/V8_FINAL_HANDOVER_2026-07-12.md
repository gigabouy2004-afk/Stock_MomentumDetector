# V8 Foundation Validation Handover

Date: 2026-07-12

Status: Mainline V8 now enforces EMA200 plus configurable MACD `8/21/5` before Setup/Momentum. Focused 20-stock/four-date validation passed. V7 remains the operational baseline until broader validation and explicit signoff.

Plain-language analysis update, 2026-07-13: `docs/V8_EXPERIMENT_ANALYSIS_BRIEF_2026-07-13.md` is now the required first-read document. It defines MACD Reset and post-Foundation scoring, separates three MACD non-confirmation states, documents the freshness-score sign defect, and lists all matters requiring user approval.

Charter reset, 2026-07-13: active design authority has moved to `docs/V8_REVISED_DEVELOPMENT_CHARTER_2026-07-13.md` and `docs/MOMENTUM_ENGINE_FOUNDATIONAL_DESIGN_STANDARD_2026-07-13.md`. The current V8 code is a frozen experimental comparator; its inherited post-Foundation rules are not automatically approved.

Rebuild workflow approval, 2026-07-13: begin with a basic V8 engine, add one indicator at a time, fully test its formula/values/scores/gates, and integrate only after explicit user approval. Checkpoint: `docs/V8_BASIC_ENGINE_REBUILD_CHECKPOINT_2026-07-13.md`.

Basic Foundation implementation, 2026-07-13: `Momentum_Detector_V8_Basic.py` now provides the standalone EMA/MACD eligibility path with no Score or post-Foundation indicators. Frozen 80-row replay and independent validation passed. Report: `docs/V8_BASIC_FOUNDATION_IMPLEMENTATION_2026-07-13.md`.

Calculation-only indicator update, corrected 2026-07-13: RSI, ADX/+DI/-DI, True Range/ATR/ATR%, OBV/OBV EMA and Aroon calculations are available only after `Foundation_Eligible = True`, with no score or gate authority. The canonical replay executed them on 25 eligible rows, skipped all 55 ineligible rows, and preserved Foundation results on 80/80 rows. Report: `docs/V8_CALCULATION_ONLY_INDICATORS_IMPLEMENTATION_2026-07-13.md`.

RSI base-layer update, 2026-07-13: RSI(14) now has configurable inclusive limits 30-65, actual-value messages and continuation authority after Foundation eligibility. The 10-symbol sample allowed AMAT and LRCX and stopped eight symbols above 65. This is functional validation, not final performance approval. Report: `docs/V8_RSI_BASE_LAYER_IMPLEMENTATION_2026-07-13.md`.

Placeholder clarification, 2026-07-13: RSI 30/65 exists only to prove that configured lower/upper cutoffs execute correctly. It is not a recommended or operationally approved range. All future indicator defaults, periods and limits must be named configuration variables with explicit placeholder/research/approved metadata.

## Start Here

Read in this order:

1. `docs/V8_REVISED_DEVELOPMENT_CHARTER_2026-07-13.md`
2. `docs/MOMENTUM_ENGINE_FOUNDATIONAL_DESIGN_STANDARD_2026-07-13.md`
3. `docs/V8_BASIC_ENGINE_REBUILD_CHECKPOINT_2026-07-13.md`
4. `docs/V8_BASIC_FOUNDATION_IMPLEMENTATION_2026-07-13.md`
5. `docs/V8_CALCULATION_ONLY_INDICATORS_IMPLEMENTATION_2026-07-13.md`
6. `docs/V8_RSI_BASE_LAYER_IMPLEMENTATION_2026-07-13.md`
7. `docs/V8_EXPERIMENT_ANALYSIS_BRIEF_2026-07-13.md`
8. `docs/V8_FOUNDATION_VALIDATION_CONCLUSION_2026-07-12.md`
9. `docs/V8_CURRENT_OUTPUT_CONTRACT_2026-07-10.md` for current-code behaviour only
10. `docs/V1_V8_EMA200_MACD_FOUNDATION_DISCOVERY_2026-07-12.md`
11. `docs/V8_COMPREHENSIVE_BACKTEST_PLAN_2026-07-12.md`

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

Detailed review found that all 25 analyzed rows received 12 freshness points because a negative distance-from-high field is compared with positive thresholds. A likely sign correction did not change a Final Decision in this sample, but the formula must be approved, corrected, tested, and replayed before downstream-score signoff.

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
