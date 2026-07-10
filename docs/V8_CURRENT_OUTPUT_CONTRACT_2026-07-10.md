# V8 Current Output Contract

Date: 2026-07-10

Status: Development baseline. V8 is not yet operational.

## Baseline Defaults

```text
DEFAULT_COUNT_X = 5
DEFAULT_SCORE_Y = 75.0
CONFIRMED_ENTRY_MIN_SCORE = 85
```

`DEFAULT_SCORE_Y` controls only the final summary inclusion threshold. It does not define or modify any final-decision score cap.

## Post-Processor Trigger Contract

Beta and future ETF post-processing are triggered by the core engine's programmed Active Momentum decision:

```text
Final_Decision == MOMENTUM_ACTIVE
AND
Score >= CONFIRMED_ENTRY_MIN_SCORE
```

The current programmed Active threshold is `85`.

The post-processors must reference `CONFIRMED_ENTRY_MIN_SCORE`, so a future reviewed change to the core Active threshold automatically carries into post-processing eligibility.

The following CLI values do not participate in the trigger:

```text
--score-y
--count-x
```

They control only final-summary presentation. An Active row remains eligible for Beta even if a tactical `--score-y` value hides it from the final summary; a rejected/waiting row never becomes Beta-eligible merely because `--score-y` is lowered.

## Score Contract

Published `Score` is always constrained to the inclusive range `0..100`.

Fixed maximum scores by final decision:

| Final decision | Maximum published Score |
|---|---:|
| `MOMENTUM_ACTIVE` | 100 |
| `MOMENTUM_PRESENT_WAIT_CONFIRMATION` | 84 |
| `REJECT` | 49 |

The default V8 final summary therefore shows the top five rows selected from published scores of `75` or higher. Rows below 75 remain available in the full execution log.

## Append-only Execution Log

Default path:

```text
D:/Tools/Stock_MomentumDetector/Processed_Data/V8_Momentum_Execution_Log.csv
```

Behavior:

- One complete row is appended for every processed ticker.
- Rows are logged before the final-summary score filter is applied.
- No-data and error rows are included with Score `0`.
- Every row is flushed, synchronized, and the file handle is closed immediately.
- A read-only application can inspect completed rows while the scan continues, subject to the reader not requesting an exclusive file lock.
- The file persists across runs.
- `Run_ID` and `Processed_At` identify each execution and row time.
- `--log-output` selects an alternative log path.

## Final Summary Output

Default base path:

```text
D:/Tools/Stock_MomentumDetector/Processed_Data/V8_Momentum_Execution_Dump.csv
```

Behavior:

- Written after the complete scan finishes.
- Contains the sorted top `--count-x` rows satisfying `Score >= --score-y`.
- Remains separate from the full append-only execution log.
- `--output` selects an alternative final-summary path.

## Current Feature State

The V8 development engine preserves corrected V7 scoring/output behavior and now contains the first Beta post-processor implementation.

Implemented in development:

- Beta is calculated from up to 252 aligned completed-session daily returns against the engine-selected benchmark.
- At least 200 aligned return observations are required.
- A live/pre-market/post-market override is excluded from Beta by using `Regular_Session_Close` when present.
- Beta executes only after the semantic Active trigger passes.
- The only production-row field written by the Beta processor is `Score_Message`.
- `Score`, `Final_Decision`, component scores, ranking, and CLI selection are unchanged by Beta.
- Missing/insufficient Beta data fails open with explanatory text for the already-Active row.
- Message wording is controlled by `config/V8_Post_Processor_Message_Map.csv`.
- V8 explicitly uses `fill_method=None` for `pct_change`, eliminating deprecated implicit forward filling.

Not yet implemented:

- Direct stock-to-ETF mapping.
- ETF text appended to `Score_Message`.

Beta remains under backtesting and review. ETF requires separate API validation and implementation. V8 remains non-operational until the complete signoff sequence is satisfied.

## Beta Backtest Trace Contract

`Backtest_Momentum_Detector_V8_Beta.py` creates a unique run folder containing:

- Stored daily stock and benchmark price inputs.
- The stock-master metadata snapshot used for sector/industry labels.
- Exact engine, Beta, message-map, and backtest source snapshots.
- Daily decision and Active-episode signal audits.
- Forward return, MAE, MFE, and realized-volatility observations.
- Beta-band interactions by market regime, sector, and industry.
- A deterministic random validation sample and separate expected-value file.
- A JSON manifest and SHA-256 checksum inventory.

`Validate_V8_Beta_Backtest.py` is a read-only offline validator. It verifies every stored hash and recomputes sampled decisions, scores, Beta, R-squared, and Beta bands from the frozen inputs/source snapshot.

## Version Isolation

V8 writes only V8-named default output files and creates V8-prefixed run IDs.

It does not write to:

```text
V7_Momentum_Execution_Log.csv
V7_Momentum_Execution_Dump.csv
```
