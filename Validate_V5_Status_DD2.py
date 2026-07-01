import argparse
import csv
import os
from pathlib import Path

import pandas as pd

import Momentum_Detector_V5 as engine

BASE_FOLDER = "D:/Tools/Stock_MomentumDetector"
DEFAULT_OUTPUT = os.path.join(BASE_FOLDER, "V5_Status_DD2_Validation.csv")
DEFAULT_SUMMARY = os.path.join(BASE_FOLDER, "V5_Status_DD2_Validation_Summary.csv")

KNOWN_ACTION_STATUSES = {
    "Actionable Momentum Candidate",
    "Watchlist Candidate",
    "Downgraded - Wait",
    "Rejected - Distribution Risk",
    "Rejected - Extended Hours Breakdown",
    "Avoid",
}

KNOWN_ENTRY_TIMING_STATUSES = {
    "Clean",
    "Wait - Daily Pullback Risk",
    "Failed - Distribution Risk",
    "Wait - Last Hour Bearish",
    "Wait - Intraday Selling",
    "Wait - Extended Hours Weakness",
    "Rejected - Extended Hours Breakdown",
    "Insufficient history",
}

KNOWN_REASON_PREFIXES = {
    "below EMA200",
    "weekly downtrend",
    "weekly flat",
    "weekly mixed",
    "weekly unknown",
    "not outperforming SPY",
    "distribution cluster",
    "excess volatility",
    "below EMA20 with deep 20D-high pullback",
    "below EMA20 with early 20D-high pullback",
    "lower high and lower low",
    "pullback on above-average volume",
    "daily distribution",
    "daily distribution below EMA20",
    "last 3H selling",
    "2+ bearish hourly candles",
    "last 1H bearish",
    "extended-hours weakness",
    "extended-hours breakdown",
}

FIELDS = [
    "Ticker",
    "D_Date",
    "D_Action_Status",
    "D_Score",
    "D_Entry_Timing_Status",
    "D_Classification_Reason",
    "D_Close",
    "D1_Date",
    "D1_Open",
    "D1_Close",
    "D1_Action_Status",
    "D1_Score",
    "D2_Date",
    "D2_Open",
    "D2_Close",
    "D2_Action_Status",
    "D2_Score",
    "Continuation_By_D2",
    "Validation_Result",
    "Validation_Note",
    "Status_String_Check",
    "Reason_String_Check",
    "Daily_Replay_Limitation",
]

SUMMARY_FIELDS = ["Metric", "Value"]


def parse_tickers(path, limit):
    df = pd.read_csv(path)
    ticker_col = "Ticker" if "Ticker" in df.columns else "Symbol" if "Symbol" in df.columns else df.columns[0]
    tickers = [engine.normalize_ticker(t) for t in df[ticker_col].dropna().tolist()]
    tickers = sorted(dict.fromkeys(tickers))
    return tickers[:limit] if limit else tickers


def validate_reason_string(reason):
    if not reason:
        return "OK"
    unknown = []
    for part in str(reason).split(" | "):
        if not any(part == known or part.startswith(f"{known} ") for known in KNOWN_REASON_PREFIXES):
            unknown.append(part)
    return "OK" if not unknown else "UNKNOWN_REASON: " + "; ".join(unknown)


def daily_timing_from_slice(calc_df):
    return engine.evaluate_intraday_timing(calc_df, pd.DataFrame(), {})


def replay_row(ticker, calc_df, idx):
    calc_slice = calc_df.iloc[: idx + 1]
    timing = daily_timing_from_slice(calc_slice)
    latest = calc_df.iloc[idx]
    scores, weekly_trend = engine.score_v5(latest)
    scores = engine.apply_commercial_readiness_score(latest, scores, weekly_trend, timing)
    long_term_status, reason = engine.classify_signal(latest, scores, weekly_trend, timing)
    return engine.build_output_row(ticker, latest, scores, weekly_trend, timing, long_term_status, reason)


def validation_for_status(action_status, continuation):
    if action_status == "Actionable Momentum Candidate":
        return (
            "PASS" if continuation else "FLAG_REVIEW",
            "Actionable status requires D+1/D+2 continuation above D close.",
        )
    if action_status == "Watchlist Candidate":
        return (
            "OBSERVE_CONTINUED" if continuation else "PASS_WATCHLIST_NO_CONFIRMATION",
            "Watchlist is not a full action call; continuation is recorded but not required.",
        )
    if action_status == "Downgraded - Wait":
        return (
            "FLAG_REVIEW" if continuation else "PASS_WAIT",
            "Wait should usually delay action; immediate continuation flags possible over-strict timing.",
        )
    if action_status in {"Rejected - Distribution Risk", "Rejected - Extended Hours Breakdown"}:
        return (
            "FLAG_REVIEW" if continuation else "PASS_REJECTED",
            "Rejected status should not show clean immediate continuation without review.",
        )
    if action_status == "Avoid":
        return (
            "FLAG_REVIEW" if continuation else "PASS_AVOID",
            "Avoid means required conditions failed; immediate continuation flags the failed reason for review.",
        )
    return "FAIL_UNKNOWN_STATUS", "Action status is not listed in the validation contract."


def build_validation_row(ticker, calc_df, d_idx):
    d = replay_row(ticker, calc_df, d_idx)
    d1 = replay_row(ticker, calc_df, d_idx + 1)
    d2 = replay_row(ticker, calc_df, d_idx + 2)

    d_close = calc_df.iloc[d_idx]["Close"]
    d1_open = calc_df.iloc[d_idx + 1]["Open"]
    d2_open = calc_df.iloc[d_idx + 2]["Open"]
    d2_close = calc_df.iloc[d_idx + 2]["Close"]
    continuation = bool(d1_open > d_close or d2_open > d_close or d2_close > d_close)
    validation_result, validation_note = validation_for_status(d["Action_Status"], continuation)

    status_check = "OK"
    if d["Action_Status"] not in KNOWN_ACTION_STATUSES:
        status_check = f"UNKNOWN_ACTION_STATUS: {d['Action_Status']}"
    elif d["Entry_Timing_Status"] not in KNOWN_ENTRY_TIMING_STATUSES:
        status_check = f"UNKNOWN_ENTRY_TIMING_STATUS: {d['Entry_Timing_Status']}"

    return {
        "Ticker": ticker,
        "D_Date": calc_df.index[d_idx].date().isoformat(),
        "D_Action_Status": d["Action_Status"],
        "D_Score": d["Score"],
        "D_Entry_Timing_Status": d["Entry_Timing_Status"],
        "D_Classification_Reason": d["Classification_Reason"],
        "D_Close": d_close,
        "D1_Date": calc_df.index[d_idx + 1].date().isoformat(),
        "D1_Open": d1_open,
        "D1_Close": calc_df.iloc[d_idx + 1]["Close"],
        "D1_Action_Status": d1["Action_Status"],
        "D1_Score": d1["Score"],
        "D2_Date": calc_df.index[d_idx + 2].date().isoformat(),
        "D2_Open": d2_open,
        "D2_Close": d2_close,
        "D2_Action_Status": d2["Action_Status"],
        "D2_Score": d2["Score"],
        "Continuation_By_D2": continuation,
        "Validation_Result": validation_result,
        "Validation_Note": validation_note,
        "Status_String_Check": status_check,
        "Reason_String_Check": validate_reason_string(d["Classification_Reason"]),
        "Daily_Replay_Limitation": "Historical intraday and extended-hours timing statuses are not replayable from daily Yahoo history.",
    }


def write_csv(path, fields, rows):
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: engine.clean_number(row.get(field, "")) for field in fields})


def summarize(rows, skipped):
    summary = [
        {"Metric": "Rows Validated", "Value": len(rows)},
        {"Metric": "Rows Skipped", "Value": skipped},
    ]
    df = pd.DataFrame(rows)
    if not df.empty:
        for status, count in df["D_Action_Status"].value_counts().sort_index().items():
            summary.append({"Metric": f"D_Action_Status={status}", "Value": int(count)})
        for result, count in df["Validation_Result"].value_counts().sort_index().items():
            summary.append({"Metric": f"Validation_Result={result}", "Value": int(count)})
        for check, count in df["Status_String_Check"].value_counts().sort_index().items():
            summary.append({"Metric": f"Status_String_Check={check}", "Value": int(count)})
        for check, count in df["Reason_String_Check"].value_counts().sort_index().items():
            summary.append({"Metric": f"Reason_String_Check={check}", "Value": int(count)})
    return summary


def main():
    parser = argparse.ArgumentParser(description="Validate V5 D/D+1/D+2 status behavior.")
    parser.add_argument("--ticker-csv", required=True)
    parser.add_argument("--date", default=None, help="Requested D date. Non-trading dates resolve to prior trading session.")
    parser.add_argument("--start-date", default=None, help="Start date for a trading-date validation range.")
    parser.add_argument("--end-date", default=None, help="End date for a trading-date validation range.")
    parser.add_argument("--period", default="2y")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    if not args.date and not (args.start_date and args.end_date):
        parser.error("Supply either --date or both --start-date and --end-date.")
    target_date = pd.Timestamp(args.date) if args.date else None
    start_date = pd.Timestamp(args.start_date) if args.start_date else None
    end_date = pd.Timestamp(args.end_date) if args.end_date else None
    tickers = parse_tickers(Path(args.ticker_csv), args.limit)
    benchmark_df = engine.fetch_daily_data(engine.BENCHMARK_TICKER, args.period)
    rows = []
    skipped = 0

    for ticker in tickers:
        print(f"Validating {ticker}...")
        try:
            df = engine.fetch_daily_data(ticker, args.period)
            if df.empty:
                skipped += 1
                continue
            calc_df = engine.calculate_v5_indicators(df, benchmark_df)
            if target_date is not None:
                eligible_positions = [i for i, date in enumerate(calc_df.index) if date <= target_date and i + 2 < len(calc_df)]
            else:
                eligible_positions = [
                    i
                    for i, date in enumerate(calc_df.index)
                    if start_date <= date <= end_date and i + 2 < len(calc_df)
                ]
            if not eligible_positions:
                skipped += 1
                continue
            if target_date is not None:
                eligible_positions = [eligible_positions[-1]]
            added = 0
            for d_idx in eligible_positions:
                if d_idx < engine.MIN_HISTORY_BARS:
                    continue
                rows.append(build_validation_row(ticker, calc_df, d_idx))
                added += 1
            if not added:
                skipped += 1
        except Exception as exc:
            skipped += 1
            print(f"Skipped {ticker}: {exc}")

    rows = sorted(rows, key=lambda row: (-engine.to_float(row["D_Score"]), str(row["Ticker"])))
    write_csv(args.output, FIELDS, rows)
    write_csv(args.summary_output, SUMMARY_FIELDS, summarize(rows, skipped))
    print(f"Rows validated: {len(rows)}")
    print(f"Rows skipped  : {skipped}")
    print(f"Output        : {args.output}")
    print(f"Summary       : {args.summary_output}")


if __name__ == "__main__":
    main()
