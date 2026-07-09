# V7 Current Output Contract

Date: 2026-07-10

## User-Facing Rule

In V7, `Score` is a final user-facing confidence score. It must not contradict `Final_Decision`.

`Score = 100` means momentum is active, confirmed, and fit to enter according to the engine rules. A row with `MOMENTUM_PRESENT_WAIT_CONFIRMATION` or `REJECT` must not publish `Score = 100`.

## Score Caps By Final Decision

| Final_Decision | Published Score Meaning | Maximum Published Score |
|---|---|---:|
| `MOMENTUM_ACTIVE` | Momentum is active now and fit to enter. | 100 |
| `MOMENTUM_PRESENT_WAIT_CONFIRMATION` | Momentum/setup may be present, but immediate confirmation is missing. | 84 |
| `REJECT` | Not valid for momentum action. | 49 |

The technical component fields remain available for audit:

- `Trend_Score`
- `Relative_Strength_Score`
- `Breakout_Score`
- `Freshness_Score`
- `Accumulation_Score`
- `Volatility_Score`
- `Weekly_Trend_Score`

Those component fields can explain why the setup looked strong internally, but the published `Score` must reflect the final actionability of the row.

## Live Phase Price Rule

V7 scoring is phase-price aware. If Yahoo provides a valid live price for one of these market states, the latest scoring bar is adjusted before indicators, final decision, and published score are calculated:

- `PRE`
- `REGULAR`
- `POST`
- `POSTPOST`

The adjusted price is written as `Close`, while the original regular-session close is retained as `Regular_Session_Close`.

Audit fields:

- `Market_State`
- `Live_Price`
- `Regular_Market_Price`
- `PreMarket_Price`
- `PostMarket_Price`
- `Regular_Session_Close`
- `Score_Price_Source`
- `Score_Price_Change_Pct`
- `Extended_Hours_Change_Pct`

This means a significant pre-market, regular-session, or post-market price shift can change trend, return, breakout, freshness, volatility, relative-strength, final decision, and published score.

## Confirmed Entry Hard Gates

V7 treats modest extension and mildly sub-1.0 relative volume as risk context, not automatic proof that momentum is inactive.

Current hard confirmation gates:

- `Score >= 85`
- `Weekly_Trend = Uptrend`
- `Entry_Timing_Status = Clean`
- `RS_126D_Excess_Pct >= 5.0`
- `ATR_Pct <= 10.0`
- `Return_5D_Pct <= 18.0`
- `Return_10D_Pct <= 30.0`
- `Relative_Volume_20 >= 0.75`
- `Close_Location_Pct >= 50.0`
