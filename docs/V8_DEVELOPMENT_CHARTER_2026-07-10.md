# V8 Development Charter

Date: 2026-07-10

Status: V8 development boundary approved; V8 is not yet operational.

## Version Decision

Version 7 is closed.

All new development occurs in Version 8 or V8-specific support files. V7 will not receive the Beta or ETF-mapping features.

V7 remains the current signed-off operational engine until the complete V8 release passes validation and receives explicit user signoff.

## V8 Feature Scope

V8 contains two ordered feature tracks:

1. Beta post-processing with complete backtesting and signoff.
2. Direct stock-to-ETF top-ten mapping after a suitable reverse-lookup API is identified and validated.

The ETF track begins after the Beta track is signed off. V8 becomes operational only after both tracks and the combined V8 regression package are signed off.

## User-Facing Contract

The user acts on one numeric field:

```text
Score
```

One additional string explains the score:

```text
Score_Message
```

Initial V8 post-processors do not create a second action score and do not modify the finalized core `Score`.

Post-processing begins only after the core engine has finalized Active Momentum:

```text
Final_Decision == MOMENTUM_ACTIVE
AND
Score >= CONFIRMED_ENTRY_MIN_SCORE
```

`CONFIRMED_ENTRY_MIN_SCORE` is currently `85`. Post-processors reference that programmed constant and the semantic Active decision; they do not hard-code a separate threshold.

CLI values such as `--score-y` and `--count-x` are tactical presentation controls only. Changing either CLI value must not enable or suppress Beta or ETF post-processing.

## V7 Freeze Boundary

No V8 development may edit:

```text
Momentum_Detector_V7.py
```

V8 must start from an explicitly recorded V7 source snapshot and then diverge only in V8 files.

Any future critical V7 production issue requires a separate explicit decision. It must not be mixed into V8 feature work.

## V7 Fork-Baseline Decision Resolved

The user approved the V8 defaults:

```text
DEFAULT_COUNT_X = 5
DEFAULT_SCORE_Y = 75.0
```

V8 was created from the corrected V7 implementation committed as:

```text
9a4b0ba Fix V7 score range and append-only execution log
```

The V8 baseline inherits:

- Published Score constrained to `0..100`.
- Fixed final-decision score caps independent of the summary filter.
- REJECT maximum of `49`.
- One append-only full execution-log row per processed ticker.
- A separate final top-X summary written after the scan.
- Run IDs and per-row processing timestamps in the execution log.

V8 deliberately changes the default final-summary threshold from the V7 diagnostic value of `0` to the approved V8 operational-development value of `75`.

## V8 File Boundary

Current V8 baseline file:

```text
Momentum_Detector_V8.py
```

Planned V8 feature implementation files:

```text
Momentum_Active_PostProcessor_V8.py
Beta_Context_V8.py
ETF_Context_V8.py
Backtest_Momentum_Detector_V8_Beta.py
Replay_V8_Beta_Run.py
Validate_V8_Beta_Random.py
config/V8_Beta_Release1_Config.json
config/V8_Post_Processor_Message_Map.csv
```

Planned V8 documentation and artifacts use `V8` in their filenames even where the approved design originated in a V7 planning document.

## Track 1: Beta Release

Beta work follows the approved execution design in:

```text
docs/V7_BETA_RELEASE1_EXECUTION_BACKTEST_PLAN_2026-07-10.md
```

For V8 execution, artifact names and engine references are translated from V7 to V8.

Required stages:

1. Freeze the selected V7 source snapshot as the V8 starting point.
2. Prove V8 baseline outputs match the selected V7 baseline before adding Beta.
3. Implement Beta outside core scoring.
4. Store immutable input data, source hashes, manifests, and random seeds.
5. Run chronological development, validation, and final holdout tests.
6. Run the three deterministic offline random-validation rounds.
7. Analyze Beta linkage with industry, sector, market regime, and actual forward price variation.
8. Prove exact Score invariance.
9. Produce the Beta research summary and signoff package.
10. Stop for explicit Beta signoff.

## Track 2: Direct ETF Mapping Release

ETF work follows the approved design in:

```text
docs/V7_BETA_ETF_ACTIVE_POSTPROCESSOR_PLAN_2026-07-10.md
```

Required behavior:

- Called only for finalized `MOMENTUM_ACTIVE` rows that satisfy the programmed `CONFIRMED_ENTRY_MIN_SCORE`.
- Direct stock-to-ETF reverse lookup.
- USA-listed ETFs only.
- Stock must be a top-ten holding in the returned ETF.
- At most three ETFs in the message.
- Highest available holding weight first.
- No pan-ETF Yahoo/yfinance loop.
- Bounded latency, caching, and fail-open message behavior.
- No change to core `Score`.

The direct API provider must pass schema, licensing, top-ten membership, US-listing, freshness, accuracy, and latency validation before integration.

## V8 Operational Signoff Gates

V8 cannot replace V7 until all gates pass:

### Baseline gate

- Selected V7 fork source recorded by commit/blob/hash.
- V8 pre-feature regression output matches the selected V7 baseline.
- V7 remains untouched.

### Beta gate

- Calculation and no-look-ahead tests pass.
- Offline replay from frozen inputs passes.
- Score invariance passes.
- Beta/industry/market linkage report completed.
- Random holdout validation completed.
- Beta `Score_Message` rules approved.

### ETF gate

- Direct API selected and approved.
- No universe scan path exists.
- Top-ten membership and USA ETF filtering verified.
- Runtime and failure behavior validated.
- ETF message format approved.

### Combined V8 gate

- Beta and ETF processors work together only for finalized `MOMENTUM_ACTIVE` rows meeting the programmed Active threshold.
- Score and core V7-derived decisions remain regression-safe.
- V8 output contract and handover are complete.
- Syntax, unit, integration, offline replay, and representative live tests pass.
- Explicit user operational signoff is recorded.

## Operational Transition

Before signoff:

```text
V7 = OPERATIONAL
V8 = DEVELOPMENT / NON-OPERATIONAL
```

After signoff:

```text
V8 = OPERATIONAL
V7 = FROZEN LEGACY BASELINE
```

The transition must be an explicit version switch. Development results alone do not make V8 operational.
