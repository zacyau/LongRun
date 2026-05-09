"""
中证红利 vs 国证A股 对比分析服务
数据源: 新浪财经 CN_MarketData.getKLineData
"""
import math
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Optional

INDEX_CONFIGS = {
    "hongli": {"symbol": "sh515180", "name": "中证红利"},
    "guozheng": {"symbol": "sz399317", "name": "国证A股"},
}


def fetch_kline_sina(symbol: str, datalen: int = 2500) -> pd.DataFrame:
    url = (
        f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
        f"/CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=5&datalen={datalen}"
    )
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return pd.DataFrame()

    records = []
    for line in data:
        records.append({
            "date": line["day"],
            "open": float(line["open"]),
            "close": float(line["close"]),
            "high": float(line["high"]),
            "low": float(line["low"]),
            "volume": float(line["volume"]),
        })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["return"] = df["close"].pct_change().fillna(0)
    df["total_return"] = (1 + df["return"]).cumprod() * 1000
    return df


def _slice_by_date(series: list, dates: list, start: Optional[str], end: Optional[str]) -> tuple:
    if not dates:
        return [], []
    start_idx = 0
    end_idx = len(dates) - 1
    if start:
        for i, d in enumerate(dates):
            if d >= start:
                start_idx = i
                break
    if end:
        for i in range(len(dates) - 1, -1, -1):
            if dates[i] <= end:
                end_idx = i
                break
    if start_idx > end_idx:
        return [], []
    return dates[start_idx:end_idx + 1], series[start_idx:end_idx + 1]


def get_all_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    dfs = {}
    for key, config in INDEX_CONFIGS.items():
        df = fetch_kline_sina(config["symbol"])
        if df.empty:
            raise Exception(f"获取 {config['name']} 数据失败")
        dfs[key] = df

    hongli = dfs["hongli"][["date", "close", "return", "total_return"]].copy()
    guozheng = dfs["guozheng"][["date", "close", "return", "total_return"]].copy()
    guozheng.columns = ["date", "guozheng_close", "guozheng_return", "guozheng_tr"]
    hongli.columns = ["date", "hongli_close", "hongli_return", "hongli_tr"]

    merged = hongli.merge(guozheng, on="date", how="inner")

    def clean(v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        return v

    def clean_list(lst):
        return [clean(x) for x in lst]

    chart1_dates_full = merged["date"].dt.strftime("%Y-%m-%d").tolist()
    chart1_hongli_full = clean_list(merged["hongli_tr"].round(4).tolist())
    chart1_guozheng_full = clean_list(merged["guozheng_tr"].round(4).tolist())

    merged["ratio"] = merged["hongli_tr"] / merged["guozheng_tr"]
    window = 242
    merged["ratio_ma"] = merged["ratio"].rolling(window=window, min_periods=1).mean()
    merged["ratio_std"] = merged["ratio"].rolling(window=window, min_periods=1).std()
    merged["upper"] = merged["ratio_ma"] + 2 * merged["ratio_std"]
    merged["lower"] = merged["ratio_ma"] - 2 * merged["ratio_std"]

    latest_full = merged.iloc[-1]
    upper_val = latest_full["upper"]
    lower_val = latest_full["lower"]
    ma_val = latest_full["ratio_ma"]
    ratio_val = latest_full["ratio"]
    pct_b = (ratio_val - lower_val) / (upper_val - lower_val) if upper_val != lower_val else 0.5
    bandwidth = (upper_val - lower_val) / ma_val * 100 if ma_val != 0 else 0

    chart2_dates_full = chart1_dates_full
    chart2_ratio_full = clean_list(merged["ratio"].round(4).tolist())
    chart2_ma242_full = clean_list(merged["ratio_ma"].round(4).tolist())
    chart2_upper_full = clean_list(merged["upper"].round(4).tolist())
    chart2_lower_full = clean_list(merged["lower"].round(4).tolist())

    merged["hongli_40d"] = merged["hongli_return"].rolling(window=40, min_periods=1).sum()
    merged["guozheng_40d"] = merged["guozheng_return"].rolling(window=40, min_periods=1).sum()
    merged["profit_diff"] = merged["hongli_40d"] - merged["guozheng_40d"]
    merged["profit_diff_ma242"] = merged["profit_diff"].rolling(window=242, min_periods=1).mean()
    mean_diff = float(merged["profit_diff"].mean())

    chart3_dates_full = chart1_dates_full
    chart3_diff_full = clean_list((merged["profit_diff"] * 100).round(4).tolist())
    chart3_diff_ma242_full = clean_list((merged["profit_diff_ma242"] * 100).round(4).tolist())

    delta = merged["ratio"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = (100 - (100 / (1 + rs))).fillna(50)
    merged["rsi14"] = rsi
    merged["rsi_ma242"] = rsi.rolling(window=242, min_periods=1).mean()
    latest_rsi = float(merged["rsi14"].iloc[-1])
    latest_rsi_ma = float(merged["rsi_ma242"].iloc[-1])

    chart4_dates_full = chart1_dates_full
    chart4_rsi_full = clean_list(merged["rsi14"].round(4).tolist())
    chart4_rsi_ma242_full = clean_list(merged["rsi_ma242"].round(4).tolist())

    sliced_dates, chart1_hongli = _slice_by_date(chart1_hongli_full, chart1_dates_full, start_date, end_date)
    _, chart1_guozheng = _slice_by_date(chart1_guozheng_full, chart1_dates_full, start_date, end_date)
    _, chart2_ratio = _slice_by_date(chart2_ratio_full, chart2_dates_full, start_date, end_date)
    _, chart2_ma242 = _slice_by_date(chart2_ma242_full, chart2_dates_full, start_date, end_date)
    _, chart2_upper = _slice_by_date(chart2_upper_full, chart2_dates_full, start_date, end_date)
    _, chart2_lower = _slice_by_date(chart2_lower_full, chart2_dates_full, start_date, end_date)
    _, chart3_diff = _slice_by_date(chart3_diff_full, chart3_dates_full, start_date, end_date)
    _, chart3_diff_ma242 = _slice_by_date(chart3_diff_ma242_full, chart3_dates_full, start_date, end_date)
    _, chart4_rsi = _slice_by_date(chart4_rsi_full, chart4_dates_full, start_date, end_date)
    _, chart4_rsi_ma242 = _slice_by_date(chart4_rsi_ma242_full, chart4_dates_full, start_date, end_date)

    sliced_len = len(sliced_dates)
    slice_ratio = ratio_val
    if sliced_len > 0:
        slice_ratio = chart2_ratio[-1] if chart2_ratio[-1] is not None else ratio_val

    pct_b_sliced = pct_b
    if upper_val != lower_val and pct_b_sliced == pct_b:
        last_upper = chart2_upper[-1] if chart2_upper[-1] is not None else upper_val
        last_lower = chart2_lower[-1] if chart2_lower[-1] is not None else lower_val
        last_ma = chart2_ma242[-1] if chart2_ma242[-1] is not None else ma_val
        last_ratio = slice_ratio if slice_ratio is not None else ratio_val
        if last_upper != last_lower and last_ma != 0:
            pct_b_sliced = (last_ratio - last_lower) / (last_upper - last_lower)

    return {
        "chart1": {
            "dates": sliced_dates,
            "hongli": chart1_hongli,
            "guozheng": chart1_guozheng,
        },
        "chart2": {
            "dates": sliced_dates,
            "ratio": chart2_ratio,
            "ma242": chart2_ma242,
            "upper": chart2_upper,
            "lower": chart2_lower,
            "pctB": round(float(pct_b_sliced), 2),
            "bandwidth": round(float(bandwidth), 2),
        },
        "chart3": {
            "dates": sliced_dates,
            "diff": chart3_diff,
            "diff_ma242": chart3_diff_ma242,
            "mean": round(mean_diff * 100, 2),
        },
        "chart4": {
            "dates": sliced_dates,
            "rsi": chart4_rsi,
            "rsi_ma242": chart4_rsi_ma242,
            "latest_rsi": round(latest_rsi, 2),
            "latest_rsi_ma": round(latest_rsi_ma, 2),
        },
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
