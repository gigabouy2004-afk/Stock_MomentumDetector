# V8 Development Charter

Original date: 2026-07-10

Updated: 2026-07-11

Status: Beta track closed and dropped; ETF information extraction is the only active V8 post-processing track. V8 remains non-operational until Phase 2 validation and explicit signoff are complete.

## Version Boundary

Version 7 is closed and remains the operational engine. New work occurs only in V8 or V8-specific support files. `Momentum_Detector_V7.py` must not be edited by the V8 ETF track.

V8 was forked from corrected V7 commit:

```text
9a4b0ba Fix V7 score range and append-only execution log
```

Approved V8 presentation defaults remain:

```text
DEFAULT_COUNT_X = 5
DEFAULT_SCORE_Y = 75.0
```

## Beta Track Final Decision

The Beta pilot produced limited descriptive differences but did not provide sufficiently conclusive, independent evidence that Beta reliably explains or predicts forward price movement after an Active Momentum signal.

User decision on 2026-07-11:

- Stop all further Beta research and validation.
- Do not use Beta in `Score`, `Final_Decision`, ranking, allocation guidance, or `Score_Message`.
- Remove the Beta processor and its active development tooling from the V8 production path.
- Preserve the canonical Beta pilot folder and report only as historical audit evidence.

The Beta track is closed without production signoff. It is not a prerequisite for the ETF track after this decision.

## Active V8 Scope: ETF Information Extraction

V8 Phase 2 provides direct stock-to-ETF information for confirmed Active Momentum stocks.

Production trigger:

```text
Final_Decision == MOMENTUM_ACTIVE
AND
Score >= CONFIRMED_ENTRY_MIN_SCORE
```

`CONFIRMED_ENTRY_MIN_SCORE` is currently `85`. The post-processor references the programmed constant. CLI values such as `--score-y` and `--count-x` are presentation controls only and cannot enable or suppress ETF processing.

## User-Facing Contract

The user acts on one numeric field:

```text
Score
```

One string provides ETF context:

```text
Score_Message
```

The ETF processor must never modify `Score`, component scores, final decisions, or ranks.

Example:

```text
Score = 92
Score_Message = Active momentum confirmed. Verified top-10 ETF mappings: SMH 19.20%; VGT 16.77%; FTEC 16.60%.
```

## Phase 2 Requirements

- One stock-specific reverse lookup per eligible Active stock.
- No pan-ETF Yahoo/yfinance holdings loop.
- No per-ETF holdings calls in the live Momentum Detector path.
- USA-listed ETFs only, using the local US ETF master as a whitelist.
- Return at most three eligible ETFs.
- Highest stock holding weight first; ETF ticker is the deterministic tie-breaker.
- Top-ten membership must be proven, never assumed.
- Bounded timeout, persistent TTL cache, explicit failure text, and fail-open behavior.
- API/source failure must leave `Score` byte-for-byte unchanged.

## Phase 2A Source Decision

The current internal implementation uses one direct TradingView stock-to-funds page:

```text
https://www.tradingview.com/symbols/<EXCHANGE>-<STOCK>/etfs/
```

The page provides ETF ticker, listing venue, and stock weight for up to 100 funds holding the stock. It is a direct stock-specific source and does not scan an ETF universe.

TradingView does not publish this page as a stable developer API contract. Therefore:

- The parser is schema-validated and fails open if the page changes.
- Raw response hashes, latency, and source URLs are recorded in validation artifacts.
- The local US ETF master filters non-US funds.
- Leveraged/inverse funds are excluded from the mathematical top-ten proof.
- The implementation is conservative and may omit valid mappings rather than display an unproven top-ten claim.

Financial Modeling Prep was reviewed as a documented direct reverse API candidate. Its published asset-exposure schema provides weights but does not document holding rank/top-ten evidence, and no entitled API key is configured locally. It was not selected for this release.

## Conservative Top-Ten Proof

For a non-leveraged portfolio with non-negative weights summing to 100%, a holding with weight greater than:

```text
100 / 11 = 9.090909...%
```

cannot have ten larger holdings ahead of it. Such a holding is therefore mathematically guaranteed to be within the top ten.

V8 returns only locally whitelisted, non-leveraged USA ETFs passing this strict test. Valid top-ten holdings with lower weights are intentionally omitted because the direct reverse page does not provide rank.

## V8 ETF Files

```text
Momentum_Detector_V8.py
ETF_Context_V8.py
Backtest_Momentum_Detector_V8_ETF.py
config/V8_Post_Processor_Message_Map.csv
tests/test_etf_context_v8.py
```

Historical Beta evidence remains under:

```text
backtests/V8_Beta_Release1/runs/V8BETA_20260710T175207Z_27cee6f_20260710
docs/V8_BETA_RELEASE1_PILOT_2026-07-10.md
```

It is not imported or executed by the active V8 engine.

## Operational Signoff Gates

V8 may replace V7 only after:

- Five-stock and representative live ETF validations pass.
- Every returned mapping is independently confirmed within the ETF's top ten during validation.
- Exactly one reverse-source request per production stock is proven.
- No production path can call per-ETF holdings pages or a yfinance ETF-universe loop.
- US whitelist, leverage exclusions, ordering, caching, timeout, and failure tests pass.
- `Score` invariance passes.
- ETF message wording is approved.
- Explicit user operational signoff is recorded.

Until then:

```text
V7 = OPERATIONAL
V8 = DEVELOPMENT / NON-OPERATIONAL
```
