import argparse
import csv
import math
import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

BASE_FOLDER = "D:/Tools/Stock_MomentumDetector"
EXECUTION_LOG_CSV = os.path.join(BASE_FOLDER, "V5_Momentum_Execution_Dump.csv")
TICKER_INPUT_CSV = Path("D:/Tools/StockCodeMaster/02_Stock/24-06-US_Common_Stocks_Master_Library-Sector-Technology.csv")

LOOKBACK_WINDOW = "5y"
BENCHMARK_TICKER = "SPY"
API_DELAY_SECONDS = 1.0
MIN_HISTORY_BARS = 300
MIN_MOMENTUM_SCORE = 70
EXTENDED_HOURS_WAIT_DROP_PCT = -2.0
EXTENDED_HOURS_REJECT_DROP_PCT = -5.0

STATUS_SORT_RANK = {
    "Momentum Candidate": 0,
    "Watchlist Candidate": 1,
    "Extended / Exhaustion Risk": 2,
    "Avoid": 3,
}

ENTRY_TIMING_SORT_RANK = {
    "Clean": 0,
    "Wait - Last Hour Bearish": 1,
    "Wait - Intraday Selling": 2,
    "Wait - Extended Hours Weakness": 3,
    "Wait - Daily Pullback Risk": 4,
    "Failed - Distribution Risk": 5,
    "Rejected - Extended Hours Breakdown": 6,
    "Insufficient history": 7,
}

ACTION_STATUS_RANK = {
    "Actionable Momentum Candidate": 1,
    "Watchlist Candidate": 2,
    "Downgraded - Wait": 3,
    "Rejected - Distribution Risk": 4,
    "Rejected - Extended Hours Breakdown": 4,
    "Avoid": 5,
}

CSV_FIELDS = [
    "Ticker", "Action_Rank", "Action_Status", "Long_Term_Status", "Entry_Timing_Status", "Classification_Reason",
    "Market_State", "Live_Price", "Regular_Market_Price", "PreMarket_Price", "PostMarket_Price",
    "Extended_Hours_Change_Pct", "Close", "Score", "Trend_Score", "Relative_Strength_Score", "Breakout_Score",
    "Accumulation_Score", "Volatility_Score", "Weekly_Stage_Score",
    "Weekly_Stage", "Weekly_Close", "Weekly_SMA_30", "Weekly_SMA_30_Slope_Pct_10W",
    "EMA_20", "EMA_50", "EMA_150", "EMA_200", "EMA_200_Slope_Pct_50D",
    "Return_63D_Pct", "Return_126D_Pct", "Return_252D_Pct", "Benchmark_Return_126D_Pct",
    "RS_126D_Excess_Pct", "RS_Ratio", "RS_SMA_50", "RS_SMA_200", "RS_Slope_Pct_50D",
    "Return_5D_Pct", "Return_10D_Pct", "High_20D", "High_55D", "High_100D", "High_252D",
    "Distance_From_20D_High_Pct", "Distance_From_52W_High_Pct", "Lower_High_Day",
    "Lower_Low_Day", "Close_Below_EMA20",
    "ATR_14", "ATR_Pct", "Volume", "Volume_Avg_50", "Accumulation_Days_50",
    "Distribution_Days_50", "Net_Accumulation_50", "Latest_Distribution_Day",
    "Daily_Change_Pct", "Last_3H_Return_Pct", "Bearish_1H_Candles_Last3", "Last_1H_Bearish",
]


def clean_number(value):
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, (int, float)) and not math.isfinite(value):
        return ""
    return value


def to_float(value):
    try:
        if value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def sort_output_rows(rows):
    return sorted(
        rows,
        key=lambda row: (
            int(to_float(row.get("Action_Rank")) or 99),
            STATUS_SORT_RANK.get(row.get("Long_Term_Status"), 99),
            ENTRY_TIMING_SORT_RANK.get(row.get("Entry_Timing_Status"), 99),
            -to_float(row.get("Score")),
            -to_float(row.get("Trend_Score")),
            str(row.get("Ticker", "")),
        ),
    )


def timestamped_output_path(path):
    base, ext = os.path.splitext(path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_{timestamp}{ext}"


def write_execution_log(rows, output_path=EXECUTION_LOG_CSV):
    sorted_rows = sort_output_rows(rows)
    output_path = os.path.abspath(output_path)
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    try:
        file = open(output_path, "w", encoding="utf-8", newline="")
    except OSError:
        output_path = timestamped_output_path(output_path)
        file = open(output_path, "w", encoding="utf-8", newline="")

    with file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in sorted_rows:
            writer.writerow({field: clean_number(row.get(field, "")) for field in CSV_FIELDS})

    return output_path, sorted_rows


def parse_ticker_values(values):
    tickers = []
    for value in values or []:
        tickers.extend(part.strip() for part in str(value).split(","))
    return [ticker for ticker in tickers if ticker]


def resolve_action_status(long_term_status, entry_timing_status):
    if entry_timing_status == "Rejected - Extended Hours Breakdown":
        action_status = "Rejected - Extended Hours Breakdown"
    elif entry_timing_status == "Failed - Distribution Risk":
        action_status = "Rejected - Distribution Risk"
    elif long_term_status == "Momentum Candidate" and entry_timing_status == "Clean":
        action_status = "Actionable Momentum Candidate"
    elif long_term_status == "Momentum Candidate":
        action_status = "Downgraded - Wait"
    elif long_term_status == "Watchlist Candidate" and entry_timing_status == "Clean":
        action_status = "Watchlist Candidate"
    elif long_term_status == "Watchlist Candidate":
        action_status = "Downgraded - Wait"
    else:
        action_status = "Avoid"
    return ACTION_STATUS_RANK[action_status], action_status


def build_status_row(ticker, long_term_status, entry_timing_status, reason=""):
    action_rank, action_status = resolve_action_status(long_term_status, entry_timing_status)
    return {
        "Ticker": ticker,
        "Action_Rank": action_rank,
        "Action_Status": action_status,
        "Long_Term_Status": long_term_status,
        "Entry_Timing_Status": entry_timing_status,
        "Classification_Reason": reason,
    }


def normalize_index(df):
    df = df.copy()
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    return df


def normalize_ticker(ticker):
    formatted = str(ticker).strip()
    if "XNSE" in formatted:
        formatted = formatted.replace("XNSE", "").replace(":", "").strip() + ".NS"
    return formatted


def fetch_daily_data(ticker, period=LOOKBACK_WINDOW):
    df = yf.download(ticker, period=period, progress=False, auto_adjust=False)
    if df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return normalize_index(df[["Open", "High", "Low", "Close", "Volume"]].dropna())


def fetch_hourly_data(ticker):
    try:
        df = yf.Ticker(ticker).history(period="5d", interval="1h", prepost=True, auto_adjust=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df[["Open", "High", "Low", "Close", "Volume"]].dropna().copy()
    except Exception:
        return pd.DataFrame()


def fetch_live_quote(ticker):
    quote = {
        "market_state": "",
        "live_price": float("nan"),
        "regular_market_price": float("nan"),
        "pre_market_price": float("nan"),
        "post_market_price": float("nan"),
    }
    try:
        info = yf.Ticker(ticker).info
    except Exception:
        return quote

    quote["market_state"] = info.get("marketState") or ""
    quote["regular_market_price"] = info.get("regularMarketPrice") or info.get("currentPrice") or float("nan")
    quote["pre_market_price"] = info.get("preMarketPrice") or float("nan")
    quote["post_market_price"] = info.get("postMarketPrice") or float("nan")

    if quote["market_state"] == "PRE" and pd.notna(quote["pre_market_price"]):
        quote["live_price"] = quote["pre_market_price"]
    elif quote["market_state"] in ["POST", "POSTPOST"] and pd.notna(quote["post_market_price"]):
        quote["live_price"] = quote["post_market_price"]
    elif pd.notna(quote["regular_market_price"]):
        quote["live_price"] = quote["regular_market_price"]

    return quote


def ema(series, span):
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def true_range(df):
    prev_close = df["Close"].shift(1)
    return pd.concat(
        [
            df["High"] - df["Low"],
            (df["High"] - prev_close).abs(),
            (df["Low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)


def calculate_v5_indicators(df, benchmark_df):
    df = df.copy()
    close = df["Close"]
    volume = df["Volume"]

    df["EMA_20"] = ema(close, 20)
    df["EMA_50"] = ema(close, 50)
    df["EMA_150"] = ema(close, 150)
    df["EMA_200"] = ema(close, 200)
    df["EMA_200_Slope_Pct_50D"] = df["EMA_200"].pct_change(50) * 100

    df["Return_5D_Pct"] = close.pct_change(5) * 100
    df["Return_10D_Pct"] = close.pct_change(10) * 100
    df["Return_63D_Pct"] = close.pct_change(63) * 100
    df["Return_126D_Pct"] = close.pct_change(126) * 100
    df["Return_252D_Pct"] = close.pct_change(252) * 100

    df["High_20D"] = df["High"].rolling(20).max()
    df["High_55D"] = df["High"].rolling(55).max()
    df["High_100D"] = df["High"].rolling(100).max()
    df["High_252D"] = df["High"].rolling(252).max()
    df["Distance_From_20D_High_Pct"] = ((close / df["High_20D"]) - 1) * 100
    df["Distance_From_52W_High_Pct"] = ((df["High_252D"] - close) / df["High_252D"]) * 100
    df["Lower_High_Day"] = df["High"] < df["High"].shift(1)
    df["Lower_Low_Day"] = df["Low"] < df["Low"].shift(1)
    df["Close_Below_EMA20"] = close < df["EMA_20"]

    df["ATR_14"] = true_range(df).rolling(14).mean()
    df["ATR_Pct"] = (df["ATR_14"] / close) * 100
    df["Volume_Avg_50"] = volume.rolling(50).mean()

    daily_change = close.pct_change() * 100
    df["Daily_Change_Pct"] = daily_change
    df["Accumulation_Day"] = (daily_change >= 1.0) & (volume > df["Volume_Avg_50"])
    df["Distribution_Day"] = (daily_change <= -1.0) & (volume > df["Volume_Avg_50"])
    df["Accumulation_Days_50"] = df["Accumulation_Day"].rolling(50).sum()
    df["Distribution_Days_50"] = df["Distribution_Day"].rolling(50).sum()
    df["Net_Accumulation_50"] = df["Accumulation_Days_50"] - df["Distribution_Days_50"]
    df["Latest_Distribution_Day"] = df["Distribution_Day"]

    benchmark_close = benchmark_df["Close"].reindex(df.index).ffill()
    df["Benchmark_Return_126D_Pct"] = benchmark_close.pct_change(126) * 100
    df["RS_126D_Excess_Pct"] = df["Return_126D_Pct"] - df["Benchmark_Return_126D_Pct"]
    df["RS_Ratio"] = close / benchmark_close
    df["RS_SMA_50"] = df["RS_Ratio"].rolling(50).mean()
    df["RS_SMA_200"] = df["RS_Ratio"].rolling(200).mean()
    df["RS_Slope_Pct_50D"] = df["RS_Ratio"].pct_change(50) * 100

    weekly = df.resample("W-FRI").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}).dropna()
    weekly["Weekly_SMA_30"] = weekly["Close"].rolling(30).mean()
    weekly["Weekly_SMA_30_Slope_Pct_10W"] = weekly["Weekly_SMA_30"].pct_change(10) * 100
    weekly_fields = weekly[["Close", "Weekly_SMA_30", "Weekly_SMA_30_Slope_Pct_10W"]].rename(columns={"Close": "Weekly_Close"})
    df = df.join(weekly_fields.reindex(df.index, method="ffill"))

    return df


def append_reason(reasons, reason):
    if reason and reason not in reasons:
        reasons.append(reason)


def evaluate_intraday_timing(daily_df, hourly_df, quote=None):
    result = {
        "status": "Clean",
        "market_state": "",
        "live_price": float("nan"),
        "regular_market_price": float("nan"),
        "pre_market_price": float("nan"),
        "post_market_price": float("nan"),
        "extended_hours_change_pct": float("nan"),
        "last_3h_return_pct": float("nan"),
        "bearish_1h_candles_last3": 0,
        "last_1h_bearish": False,
        "reason": "",
    }

    latest = daily_df.iloc[-1]
    reasons = []
    quote = quote or {}
    result["market_state"] = quote.get("market_state", "")
    result["live_price"] = quote.get("live_price", float("nan"))
    result["regular_market_price"] = quote.get("regular_market_price", float("nan"))
    result["pre_market_price"] = quote.get("pre_market_price", float("nan"))
    result["post_market_price"] = quote.get("post_market_price", float("nan"))

    if result["market_state"] in ["PRE", "POST", "POSTPOST"] and pd.notna(result["live_price"]) and latest["Close"]:
        result["extended_hours_change_pct"] = ((result["live_price"] / latest["Close"]) - 1) * 100
        if result["extended_hours_change_pct"] <= EXTENDED_HOURS_REJECT_DROP_PCT:
            result["status"] = "Rejected - Extended Hours Breakdown"
            append_reason(reasons, f"extended-hours breakdown {result['extended_hours_change_pct']:.2f}%")
        elif result["extended_hours_change_pct"] <= EXTENDED_HOURS_WAIT_DROP_PCT:
            result["status"] = "Wait - Extended Hours Weakness"
            append_reason(reasons, f"extended-hours weakness {result['extended_hours_change_pct']:.2f}%")

    daily_pullback = (
        latest["Close_Below_EMA20"]
        and latest["Distance_From_20D_High_Pct"] <= -8
        and latest["Return_5D_Pct"] <= -3
    )
    lower_high_low = bool(latest["Lower_High_Day"] and latest["Lower_Low_Day"])
    high_volume_pullback = bool(latest["Volume"] > latest["Volume_Avg_50"] and latest["Daily_Change_Pct"] <= 0.5)

    if daily_pullback:
        append_reason(reasons, "below EMA20 with deep 20D-high pullback")
    if lower_high_low:
        append_reason(reasons, "lower high and lower low")
    if high_volume_pullback:
        append_reason(reasons, "pullback on above-average volume")

    if result["status"] == "Clean" and daily_pullback and (lower_high_low or high_volume_pullback):
        result["status"] = "Wait - Daily Pullback Risk"

    if hourly_df.empty or len(hourly_df) < 3:
        result["reason"] = " | ".join(reasons)
        return result

    last_3h = hourly_df.tail(3)
    first_open = last_3h["Open"].iloc[0]
    last_close = last_3h["Close"].iloc[-1]
    result["last_3h_return_pct"] = ((last_close / first_open) - 1) * 100 if first_open else float("nan")
    result["bearish_1h_candles_last3"] = int((last_3h["Close"] < last_3h["Open"]).sum())
    result["last_1h_bearish"] = bool(last_3h["Close"].iloc[-1] < last_3h["Open"].iloc[-1])

    daily_drop = latest["Daily_Change_Pct"]
    if pd.notna(daily_drop) and daily_drop <= -3:
        append_reason(reasons, "daily distribution")
    if result["last_3h_return_pct"] <= -1:
        append_reason(reasons, "last 3H selling")
    if result["bearish_1h_candles_last3"] >= 2:
        append_reason(reasons, "2+ bearish hourly candles")
    if result["last_1h_bearish"]:
        append_reason(reasons, "last 1H bearish")

    if result["status"] != "Rejected - Extended Hours Breakdown" and "daily distribution" in reasons and result["bearish_1h_candles_last3"] >= 2:
        result["status"] = "Failed - Distribution Risk"
    elif result["status"] == "Clean" and result["last_3h_return_pct"] <= -1 and result["bearish_1h_candles_last3"] >= 2:
        result["status"] = "Wait - Intraday Selling"
    elif result["status"] == "Clean" and result["last_1h_bearish"]:
        result["status"] = "Wait - Last Hour Bearish"
    result["reason"] = " | ".join(reasons)
    return result


def classify_weekly_stage(row):
    if pd.isna(row["Weekly_SMA_30"]) or pd.isna(row["Weekly_SMA_30_Slope_Pct_10W"]):
        return "Unknown"
    if row["Weekly_Close"] > row["Weekly_SMA_30"] and row["Weekly_SMA_30_Slope_Pct_10W"] > 0:
        return "Stage 2"
    if row["Weekly_Close"] < row["Weekly_SMA_30"] and row["Weekly_SMA_30_Slope_Pct_10W"] < 0:
        return "Stage 4"
    if abs(row["Weekly_SMA_30_Slope_Pct_10W"]) <= 1:
        return "Stage 1/3"
    return "Transition"


def score_v5(row):
    scores = {"trend": 0, "relative_strength": 0, "breakout": 0, "accumulation": 0, "volatility": 0, "weekly_stage": 0}

    if row["Close"] > row["EMA_50"] > row["EMA_150"] > row["EMA_200"]:
        scores["trend"] += 20
    elif row["Close"] > row["EMA_200"] and row["EMA_50"] > row["EMA_200"]:
        scores["trend"] += 12
    if row["EMA_200_Slope_Pct_50D"] > 2:
        scores["trend"] += 10
    elif row["EMA_200_Slope_Pct_50D"] > 0:
        scores["trend"] += 5

    if row["RS_126D_Excess_Pct"] > 20:
        scores["relative_strength"] += 12
    elif row["RS_126D_Excess_Pct"] > 5:
        scores["relative_strength"] += 8
    elif row["RS_126D_Excess_Pct"] > 0:
        scores["relative_strength"] += 4
    if row["RS_Ratio"] > row["RS_SMA_50"] > row["RS_SMA_200"] and row["RS_Slope_Pct_50D"] > 0:
        scores["relative_strength"] += 13

    if row["Close"] >= row["High_55D"] * 0.98:
        scores["breakout"] += 6
    if row["Close"] >= row["High_100D"] * 0.97:
        scores["breakout"] += 6
    if row["Distance_From_52W_High_Pct"] <= 10:
        scores["breakout"] += 8
    elif row["Distance_From_52W_High_Pct"] <= 20:
        scores["breakout"] += 4

    if row["Net_Accumulation_50"] >= 3:
        scores["accumulation"] += 10
    elif row["Net_Accumulation_50"] > 0:
        scores["accumulation"] += 6
    if row["Distribution_Days_50"] <= 5:
        scores["accumulation"] += 5
    elif row["Distribution_Days_50"] >= 10:
        scores["accumulation"] -= 5
    if row["Latest_Distribution_Day"]:
        scores["accumulation"] -= 8

    if row["ATR_Pct"] <= 4:
        scores["volatility"] += 10
    elif row["ATR_Pct"] <= 7:
        scores["volatility"] += 7
    elif row["ATR_Pct"] <= 10:
        scores["volatility"] += 3
    elif row["ATR_Pct"] > 15:
        scores["volatility"] -= 5

    stage = classify_weekly_stage(row)
    if stage == "Stage 2":
        scores["weekly_stage"] += 15
    elif stage == "Transition":
        scores["weekly_stage"] += 5
    elif stage == "Stage 4":
        scores["weekly_stage"] -= 10

    scores["final"] = min(100, max(0, sum(scores.values())))
    return scores, stage


def classify_signal(row, scores, stage, timing):
    reasons = []
    if row["Close"] <= row["EMA_200"]:
        reasons.append("below EMA200")
    if stage != "Stage 2":
        reasons.append(f"weekly {stage}")
    if row["RS_126D_Excess_Pct"] <= 0:
        reasons.append("not outperforming SPY")
    if row["Distribution_Days_50"] >= 8:
        reasons.append("distribution cluster")
    if row["ATR_Pct"] > 15:
        reasons.append("excess volatility")

    if reasons:
        long_term_status = "Avoid"
    elif scores["final"] >= 85 and timing["status"] == "Clean":
        long_term_status = "Momentum Candidate"
    elif scores["final"] >= MIN_MOMENTUM_SCORE:
        long_term_status = "Watchlist Candidate"
    elif row["Distance_From_52W_High_Pct"] <= 5 and row["ATR_Pct"] > 10:
        long_term_status = "Extended / Exhaustion Risk"
    else:
        long_term_status = "Avoid"

    return long_term_status, " | ".join(reasons) if reasons else timing["reason"]


def build_output_row(ticker, row, scores, stage, timing, long_term_status, reason):
    action_rank, action_status = resolve_action_status(long_term_status, timing["status"])
    output = {
        "Ticker": ticker,
        "Action_Rank": action_rank,
        "Action_Status": action_status,
        "Long_Term_Status": long_term_status,
        "Entry_Timing_Status": timing["status"],
        "Classification_Reason": reason,
        "Market_State": timing["market_state"],
        "Live_Price": timing["live_price"],
        "Regular_Market_Price": timing["regular_market_price"],
        "PreMarket_Price": timing["pre_market_price"],
        "PostMarket_Price": timing["post_market_price"],
        "Extended_Hours_Change_Pct": timing["extended_hours_change_pct"],
        "Score": scores["final"],
        "Trend_Score": scores["trend"],
        "Relative_Strength_Score": scores["relative_strength"],
        "Breakout_Score": scores["breakout"],
        "Accumulation_Score": scores["accumulation"],
        "Volatility_Score": scores["volatility"],
        "Weekly_Stage_Score": scores["weekly_stage"],
        "Weekly_Stage": stage,
        "Last_3H_Return_Pct": timing["last_3h_return_pct"],
        "Bearish_1H_Candles_Last3": timing["bearish_1h_candles_last3"],
        "Last_1H_Bearish": timing["last_1h_bearish"],
    }
    for field in CSV_FIELDS:
        if field not in output and field in row:
            output[field] = row[field]
    return {field: clean_number(output.get(field, "")) for field in CSV_FIELDS}


def load_tickers(ticker_csv=TICKER_INPUT_CSV):
    if not os.path.exists(ticker_csv):
        return []
    tickers_df = pd.read_csv(ticker_csv)
    ticker_col = "Ticker" if "Ticker" in tickers_df.columns else "Symbol" if "Symbol" in tickers_df.columns else tickers_df.columns[0]
    return tickers_df[ticker_col].dropna().tolist()


def resolve_tickers(cli_tickers, ticker_csv):
    tickers = parse_ticker_values(cli_tickers)
    if tickers:
        return tickers, "CLI ticker list"
    input_csv = Path(ticker_csv) if ticker_csv else TICKER_INPUT_CSV
    return load_tickers(input_csv), str(input_csv)


def main():
    parser = argparse.ArgumentParser(description="Momentum Detector V5 - Stage/RS/Breakout Momentum Engine")
    parser.add_argument("--tickers", nargs="*", default=[], help="Ticker list. Accepts space-separated and/or comma-separated values, e.g. AAPL MSFT or AAPL,MSFT.")
    parser.add_argument("--ticker-csv", default=None, help="CSV file containing ticker codes. Used when --tickers is not supplied.")
    parser.add_argument("--output", default=EXECUTION_LOG_CSV, help="Fully qualified output CSV path. Defaults to EXECUTION_LOG_CSV.")
    args = parser.parse_args()

    tickers, ticker_source = resolve_tickers(args.tickers, args.ticker_csv)
    tickers = sorted([normalize_ticker(t) for t in tickers if str(t).strip()])
    if not tickers:
        print("No tickers supplied and ticker CSV not available.")
        return

    benchmark_df = fetch_daily_data(BENCHMARK_TICKER, LOOKBACK_WINDOW)
    rows = []
    candidates = []
    watchlist = []

    print("Starting Momentum Detector V5 scan...")
    print(f"Ticker Source: {ticker_source}")
    print(f"Output Target: {args.output}")
    for ticker in tickers:
        print(f"Processing {ticker}...")
        time.sleep(API_DELAY_SECONDS)
        try:
            df = fetch_daily_data(ticker, LOOKBACK_WINDOW)
            if df.empty or len(df) < MIN_HISTORY_BARS:
                rows.append(build_status_row(ticker, "Avoid", "Insufficient history"))
                continue
            calc_df = calculate_v5_indicators(df, benchmark_df)
            timing = evaluate_intraday_timing(calc_df, fetch_hourly_data(ticker), fetch_live_quote(ticker))
            row = calc_df.iloc[-1]
            scores, stage = score_v5(row)
            long_term_status, reason = classify_signal(row, scores, stage, timing)
            output = build_output_row(ticker, row, scores, stage, timing, long_term_status, reason)
            rows.append(output)
            if long_term_status == "Momentum Candidate" and timing["status"] == "Clean":
                candidates.append(output)
            elif long_term_status in ["Momentum Candidate", "Watchlist Candidate"]:
                watchlist.append(output)
        except Exception as exc:
            rows.append(build_status_row(ticker, "Avoid", f"Error: {exc}", str(exc)))

    output_path, sorted_rows = write_execution_log(rows, args.output)

    candidates = [row for row in sorted_rows if row["Action_Status"] == "Actionable Momentum Candidate"]
    watchlist = [
        row
        for row in sorted_rows
        if row["Action_Status"] in ["Watchlist Candidate", "Downgraded - Wait", "Rejected - Distribution Risk"]
    ]
    print("============================================================")
    print("=== MOMENTUM DETECTOR V5 COMPLETE ===")
    print("============================================================")
    print(f"Total Processed : {len(rows)}")
    print(f"Clean Candidates: {len(candidates)}")
    print(f"Watchlist/Wait  : {len(watchlist)}")
    for i, row in enumerate(candidates, 1):
        print(f"{i}. {row['Ticker']:<8} | {row['Action_Status']:<30} | Score: {row['Score']}/100 | Entry: {row['Entry_Timing_Status']}")
    if watchlist:
        print("Watchlist / wait-for-entry names:")
        for i, row in enumerate(watchlist, 1):
            print(f"{i}. {row['Ticker']:<8} | {row['Action_Status']:<30} | Score: {row['Score']}/100 | Entry: {row['Entry_Timing_Status']}")
    print(f"-> Output: {output_path}")


if __name__ == "__main__":
    main()
