# V8 Revised Development Charter

Effective date: 2026-07-13

Authority: this document is the controlling development charter for V8. It supersedes `docs/V8_DEVELOPMENT_CHARTER_2026-07-10.md` for all new design, implementation, testing and approval decisions. The older charter remains historical audit evidence only.

Status: V8 is a development engine. V7 remains the operational engine. The present V8 code contains both validated infrastructure and unapproved experimental decision rules. Code existence does not constitute design approval.

User workflow confirmation, 2026-07-13: rebuild V8 from a basic engine, introduce indicators individually, fully functionally test and backtest every proposed value/score/gate, and integrate an indicator into main V8 only after explicit approval. Detailed checkpoint: `docs/V8_BASIC_ENGINE_REBUILD_CHECKPOINT_2026-07-13.md`.

Implementation update, 2026-07-13: the standalone Foundation-only engine is implemented in `Momentum_Detector_V8_Basic.py` and validated in `docs/V8_BASIC_FOUNDATION_IMPLEMENTATION_2026-07-13.md`. It contains no post-Foundation Score or indicator authority and does not replace the legacy comparator or V7.

Calculation-layer update, 2026-07-13: raw RSI, ADX/DMI, True Range/ATR, OBV and Aroon calculations were added with explicit `CALCULATION_ONLY` authority and a hard `Foundation_Eligible = True` entry prerequisite. The corrected 80-row replay executed the indicator module for all 25 eligible rows, skipped all 55 ineligible rows, and preserved Foundation results on 80/80 rows. Report: `docs/V8_CALCULATION_ONLY_INDICATORS_IMPLEMENTATION_2026-07-13.md`.

RSI base-layer update, 2026-07-13: RSI(14) is the first indicator with a configurable continuation rule. The inclusive 30-65 limits, actual-value messages and continuation Boolean passed functional and independent replay validation. This authorizes the base-layer mechanics only; whether the range improves D+1/D+5/D+8 performance remains subject to isolated RSI backtesting. Report: `docs/V8_RSI_BASE_LAYER_IMPLEMENTATION_2026-07-13.md`.

Companion standard: `docs/MOMENTUM_ENGINE_FOUNDATIONAL_DESIGN_STANDARD_2026-07-13.md` defines what is carried forward, rejected, research-only, and required to pass backtesting before entering an operational decision path.

## 1. Mission

V8 is intended to identify stocks entering credible multi-session momentum suitable for trades lasting approximately three trading sessions to one or two weeks.

V8 is not intended to predict intraday price fluctuations. Its primary validation question is whether an eligible signal produces positive movement from the next trading session's open to that session's close. Longer D+5 and D+8 measurements determine whether the move persists.

The engine must favour a small, understandable and evidence-supported design over a large collection of conventional indicators.

## 2. User Intent That Governs the Design

The governing requirements are:

1. A credible momentum stock must first have a valid long-term and current-momentum Foundation.
2. EMA200 and MACD are the intended Foundation elements inherited from the V1-V3 architecture.
3. The engine targets multi-day momentum, not intraday trading.
4. D+1 direction is the primary immediate validation; D+5 and D+8 are persistence references.
5. Technology is the primary application sector, with industrial stocks as a second intended sector.
6. A technology stock must not be rejected merely because the broad SPY index behaves differently.
7. ETF mapping is informational portfolio context only. It must never add to Score or determine Active, Wait or Reject.
8. Every term and every decision reason must be understandable without private conversation context.
9. No indicator may enter the operational path on the strength of generic claims about professional trading practice.
10. Every rule that can change a decision must be functionally and historically tested before mainstream adoption.

## 3. Operational Boundary

```text
V7 = operational baseline
V8 = development and evidence generation
```

V8 may not replace V7 until:

- all correctness defects affecting decisions or scores are closed;
- every decision-changing rule has passed its declared functional and backtest gates;
- technology and industrial calibration evidence is complete;
- an untouched chronological and ticker holdout is complete;
- historical/live limitations are documented and accepted;
- outputs expose the full decision path;
- the user explicitly approves operational promotion.

No commit, test pass, or encouraging sample result can substitute for explicit user approval.

## 4. Current V8 Reality

The current V8 implementation performs:

```text
EMA200 + configurable MACD Foundation
    -> legacy V4-V7-style Setup/Momentum scoring
    -> commercial score caps and hard classifications
    -> entry-confirmation gates
    -> Active-only external and ETF context
```

The Foundation implementation and its no-look-ahead mechanics passed focused validation.

The post-Foundation rules did not earn equivalent design approval. The 20-stock experiment showed that they reject many Foundation-qualified stocks that subsequently rise. They must be treated as a frozen comparator, not as an accepted blueprint for the new engine.

Known scoring defect:

- `Distance_From_20D_High_Pct` is stored as zero or negative, while the freshness thresholds are applied as positive upper bounds.
- All 25 fully analysed Foundation-valid rows consequently received 12 freshness points.
- A provisional sign correction did not change the five Active decisions in the focused run, but the formula remains incorrect and unapproved.

Current-code contract and approved-design contract are therefore different:

```text
Current code = reproducible experimental comparator
Approved design = Foundation plus only those later rules that independently pass promotion testing
```

## 5. Required Engine Architecture

### Stage 0 — Data integrity

Before any signal calculation:

- verify symbol normalization and exchange;
- require sufficient history for EMA200 and all configured indicators;
- use point-in-time data only;
- prevent future bars from affecting earlier signals;
- record price adjustment and corporate-action policy;
- record missing data and API failures explicitly.

Failure at Stage 0 produces an insufficient-data state, not a fabricated score.

### Stage 1 — Foundation

The carried-forward Foundation architecture is:

```text
Close > EMA200
AND configured MACD state
```

The current development baseline uses bullish-positive MACD `8/21/5`:

```text
MACD Line > Signal Line
AND MACD Line > 0
```

EMA200 plus configurable MACD is carried forward as the Foundation concept. The exact MACD periods and treatment of non-confirming MACD substates remain subject to wider backtesting.

The Foundation awards no points. It declares eligibility and state.

### Stage 2 — Evidence capture

For Foundation-qualified stocks, the engine may calculate additional indicators. Calculation alone gives an indicator no authority over the decision.

This is a hard execution boundary, not merely a decision rule. If `Foundation_Eligible = False`, the engine must stop before the post-Foundation indicator module; the post-Foundation values must remain blank and the reason for skipping must be recorded.

Every additional indicator begins as one of:

```text
INFORMATION_ONLY
RESEARCH_ONLY
```

Examples include relative strength, weekly trend, distribution count, breakout proximity, volatility, relative volume and daily close location.

### Stage 3 — Evidence-supported candidate assessment

Only rules that have passed promotion tests may influence ranking, WAIT or rejection.

Each rule must have an explicit authority level:

```text
LEVEL 0: display only
LEVEL 1: warning/message
LEVEL 2: ranking or score input
LEVEL 3: WAIT condition
LEVEL 4: hard rejection/veto
```

A rule may receive only the lowest authority justified by evidence. A hard veto requires evidence specifically showing that excluded observations have materially worse outcomes or unacceptable risk.

### Stage 4 — Entry decision

The engine publishes one unambiguous state:

- Active: all approved eligibility and entry requirements passed.
- Wait: the setup remains relevant but a defined confirmation is absent.
- Reject: a tested structural or risk-invalidating condition failed.
- Insufficient Data: the calculation cannot be trusted.

Wait and Reject are eligibility states, not predictions that price will decline.

### Stage 5 — Context enrichment

External analyst, event and ETF information may be added only after the stock decision is complete.

Context enrichment must not change:

- Foundation state;
- component measurements;
- Score;
- Active/Wait/Reject;
- ordering or rank.

ETF mapping has no predictive mandate. It is not required to prove that ETF membership predicts returns. Its mandate is only to provide accurate, bounded, clearly dated portfolio context for an already completed stock decision.

## 6. Benchmark Policy

Universal SPY veto logic is rejected.

SPY may be retained as broad-market context, but it cannot automatically reject every stock or block every Active decision.

Any relative-strength feature must specify:

- why the benchmark is appropriate for the stock;
- whether the benchmark is broad market, sector or industry;
- the measurement horizon;
- the authority requested for the feature;
- evidence that the feature improves the declared endpoint.

Technology research may compare, for example, broad technology, semiconductor, software or cybersecurity references where appropriate. Industrial research requires its own appropriate reference. Benchmark selection logic itself must be frozen and tested; benchmarks may not be chosen after viewing outcomes.

Until such testing passes, benchmark comparisons are information-only.

## 7. Score Policy

An opaque single Score is not an acceptable decision explanation.

If a composite score is retained, output must separately expose:

```text
Raw component values
Raw component points
Raw total
Every cap applied
Score after caps
Hard classification reasons
Entry-confirmation blockers
Final published score
Final decision
```

No score component is approved merely because it existed in V4-V7 or appears in the current V8 code.

No post-decision cap may conceal the score that existed before the decision. A displayed 84 for Wait or 49 for Reject must not be mistaken for the raw calculation.

Score thresholds and component weights must be configuration-versioned and evidence-linked.

## 8. ETF Policy

ETF mapping is permanently outside momentum qualification and scoring unless the user explicitly changes this charter.

Approved ETF functions:

- identify verified direct ETF exposure for an already Active stock;
- show at most the configured number of eligible mappings;
- show holding weight, source and evidence date;
- exclude unverified, leveraged or inverse mappings according to the ETF contract;
- fail open without changing the stock decision;
- preserve Score byte-for-byte.

Rejected ETF functions:

- adding points to a stock;
- confirming or rejecting momentum;
- changing rank;
- implying that ETF ownership caused or predicts the stock move;
- applying current holdings retrospectively without appropriately dated evidence.

ETF functionality requires mapping-accuracy and failure-behaviour tests, not a predictive-return test.

## 9. Backtest Outcome Contract

For signal day D:

- entry price is the next trading session's open;
- D+1 outcome exits at that next session's close;
- D+5 exits at the fifth trading session's close;
- D+8 exits at the eighth trading session's close.

D+1 is the primary directional endpoint. D+5 and D+8 measure persistence.

Every report must state:

- numerator and denominator;
- positive rate;
- mean and median return;
- benchmark context where relevant, never as an undisclosed veto;
- maximum adverse and favourable excursion when available;
- sample construction;
- sector and regime;
- whether the sample is calibration or untouched holdout;
- limitations including costs, slippage, stops and missing intraday data.

## 10. Development Lifecycle

Every proposed rule follows this lifecycle:

```text
PROPOSED
  -> FORMULA_VERIFIED
  -> INFORMATION_ONLY
  -> FROZEN_BACKTEST
  -> CALIBRATION_EVIDENCE
  -> UNTOUCHED_HOLDOUT
  -> USER_APPROVED
  -> MAINSTREAM
```

Rules may also become:

```text
REJECTED
RETIRED
```

Requirements by stage:

### Proposed

- plain-language purpose;
- exact formula;
- expected benefit;
- expected failure modes;
- requested authority level.

### Formula verified

- boundary-value unit tests;
- independent recomputation;
- missing/NaN behaviour;
- no-look-ahead test;
- configuration validation.

### Frozen backtest

- predeclared tickers, dates, horizons and variants;
- frozen inputs and source snapshot;
- one-change-at-a-time comparison;
- immutable outputs and checksums;
- independent validator.

### Calibration evidence

- adequate observations for the requested authority;
- technology and, where intended, industrial analysis;
- multiple market conditions;
- false-positive and false-negative cohorts;
- outcome and risk reporting.

### Untouched holdout

- tickers and dates not used to select the formula or threshold;
- same frozen evaluator;
- no threshold changes after results are viewed.

### User approved

- result summarized in plain language;
- trade-offs disclosed;
- exact code/config change identified;
- explicit approval recorded before mainstream integration.

## 11. Evidence Rules

The following are mandatory:

1. A rule must be tested against a minimal baseline and the current comparator.
2. Only one conceptual change may be attributed to a comparison arm.
3. Dates and tickers must be frozen before forward outcomes are opened.
4. Calibration evidence and final holdout evidence must be separate.
5. Small denominators must be shown, not hidden behind percentages.
6. A technically passing validator proves implementation integrity, not predictive success.
7. A good result in one quarter does not establish multi-regime validity.
8. A rule that excludes winners must report those false negatives explicitly.
9. A rule proposed as a veto must demonstrate veto-level evidence; otherwise it remains a warning or WAIT condition.
10. Results must be reproducible offline from frozen inputs.
11. Negative or inconclusive findings must remain in the record.
12. No generic market convention may be cited as substitute evidence.

## 12. Change-Control Rules

- V7 remains untouched by V8 experiments.
- V8 behavioural changes require versioned configuration and documentation.
- Experimental code must not silently replace the comparator.
- Frozen run folders must not be edited after checksums are written.
- Any correction that changes historical results requires a new run ID; old evidence remains preserved.
- Mainstream changes require scoped commits with test and evidence references.
- Unrelated dirty-worktree changes must not be included.
- No feature may be described as approved when it is merely implemented.

## 13. Current Carried, Rejected and Research Boundaries

Carried forward now:

- multi-day engine objective;
- point-in-time/no-look-ahead processing;
- staged Foundation-first architecture;
- EMA200 plus configurable MACD as the Foundation concept;
- D+1/D+5/D+8 outcome contract;
- transparent failure and append-only logging;
- immutable evidence and independent validation;
- ETF as Active-only informational context;
- V7 operational boundary.

Rejected now:

- universal SPY hard rejection;
- ETF influence on Score or decision;
- generic professional-practice claims as validation;
- automatic mainstream entry for inherited indicators;
- opaque Score as the sole explanation;
- ambiguous “MACD reset” terminology;
- retrospective ETF claims without dated evidence;
- operational conclusions from the five-Active sample.

Research-only until tested:

- exact MACD periods and non-confirmation state policy;
- moving-average stack and EMA200 slope beyond the Foundation;
- sector/industry relative strength and horizon;
- weekly trend;
- distribution and accumulation logic;
- breakout and recent-high proximity;
- volatility and ATR limits;
- volume and close-location confirmation;
- liquidity thresholds;
- intraday and extended-hours confirmation;
- any composite score, cap or hard veto.

The companion design standard contains the full rule-by-rule register.

## 14. Immediate Work Sequence

No new indicator should be added before these steps:

1. approve this charter and the companion design standard;
2. freeze the present V8 code as the legacy post-Foundation comparator;
3. correct and unit-test the freshness formula in an experimental path;
4. create a minimal Foundation-only candidate baseline;
5. expose raw values, points, caps and blockers;
6. replay the same frozen 80 observations for an apples-to-apples correctness comparison;
7. test one post-Foundation rule at a time, beginning with distribution authority and benchmark policy;
8. freeze a broader technology/industrial calibration set;
9. freeze a separate untouched holdout;
10. request explicit user approval for each rule proposed for mainstream authority.

## 15. Current Evidence

Canonical Foundation experiment:

```text
backtests/V8_Foundation_Validation/runs/V8FOUND_20260712T182945Z_cf0c908
```

Key result:

```text
Foundation Valid: 25 observations
D+1 positive: 19/25
D+5 positive: 23/25
D+8 positive: 18/25

Current full V8 Active: 5 observations
D+1 positive: 4/5
D+5 positive: 5/5
D+8 positive: 4/5

Foundation Valid but later Rejected: 18 observations
D+1 positive: 13/18
D+5 positive: 16/18
D+8 positive: 14/18
```

Interpretation:

- the Foundation concept is promising and suitable for continued testing;
- the current post-Foundation veto structure is not approved;
- five Active observations are insufficient for operational inference;
- ETF mapping functionality passed but remains unrelated to signal quality.

## 16. Required Reading for a Fresh Session

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
10. the frozen run manifest and validation summary

Do not use the 2026-07-10 charter as current design authority.

## 17. Charter Decision Boundary

At the effective date:

```text
V7 operational status: unchanged
V8 operational approval: not granted
Foundation concept: carried forward for continued evidence
8/21/5: current development baseline, not proven universal optimum
Current post-Foundation scoring/vetoes: comparator only, not approved design
Universal SPY veto: rejected
ETF scoring: prohibited
Next mainstream code change: blocked until charter/design-standard approval and declared functional tests
```
