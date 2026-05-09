"""
趋势信号服务
数据源: 新浪财经
MACD-V 指标 + RSI14 买卖信号
"""
import math
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from typing import Optional


_COMMON_STOCKS = {
    "贵州茅台": "sh600519", "茅台": "sh600519",
    "中国平安": "sh601318", "平安": "sh601318",
    "招商银行": "sh600036",
    "万科A": "sz000002", "万科": "sz000002",
    "格力电器": "sz000651", "格力": "sz000651",
    "美的集团": "sz000333", "美的": "sz000333",
    "比亚迪": "sz002594",
    "宁德时代": "sz300750", "宁德": "sz300750",
    "中国中免": "sh601888", "中免": "sh601888",
    "隆基绿能": "sh601012", "隆基": "sh601012",
    "五粮液": "sz000858",
    "泸州老窖": "sz000568",
    "海天味业": "sh603288", "海天": "sh603288",
    "伊利股份": "sh600887", "伊利": "sh600887",
    "恒瑞医药": "sh600276", "恒瑞": "sh600276",
    "中信证券": "sh600030", "中信": "sh600030",
    "东方财富": "sz300059", "东财": "sz300059",
    "同花顺": "sz300033",
    "光大证券": "sh601788",
    "海通证券": "sh600837",
    "中信建投": "sh601066",
    "中国中车": "sh601766", "中车": "sh601766",
    "工商银行": "sh601398", "工行": "sh601398",
    "建设银行": "sh601939",
    "中国银行": "sh601988",
    "农业银行": "sh601288",
    "交通银行": "sh601328",
    "浦发银行": "sh600000",
    "兴业银行": "sh601166",
    "民生银行": "sh600016",
    "平安银行": "sz000001",
    "华夏银行": "sh600015",
    "招商证券": "sh600999",
    "华泰证券": "sh601688",
    "国泰君安": "sh601211",
    "中国神华": "sh601088",
    "中国石油": "sh601857",
    "中国石化": "sh600028",
    "中国建筑": "sh601668",
    "中国中铁": "sh601390",
    "中国铁建": "sh601186",
    "中国电建": "sh601669",
    "中国交建": "sh601800",
    "中国化学": "sh601117",
    "中国核电": "sh601985",
    "中国国航": "sh601111",
    "中国东航": "sh600115",
    "中国南航": "sh600029",
    "南方航空": "sh600029",
    "东方航空": "sh600115",
    "顺丰控股": "sz002352", "顺丰": "sz002352",
    "海康威视": "sz002415", "海康": "sz002415",
    "中兴通讯": "sz000063", "中兴": "sz000063",
    "三一重工": "sh600031", "三一": "sh600031",
    "中联重科": "sz000157",
    "徐工机械": "sz000425",
    "柳工": "sz000528",
    "宝钢股份": "sh600019", "宝钢": "sh600019",
    "鞍钢股份": "sz000898",
    "华菱钢铁": "sz000932",
    "新希望": "sz000876",
    "温氏股份": "sz300498",
    "牧原股份": "sz002714",
    "海大集团": "sz002311",
    "双汇发展": "sz000895",
    "用友网络": "sh600588", "用友": "sh600588",
    "宝信软件": "sh600845",
    "恒生电子": "sh600570",
    "广联达": "sz002410",
    "金山办公": "sh688111",
    "沪电股份": "sz002463",
    "深南电路": "sz002916",
    "生益科技": "sh600183",
    "三安光电": "sh600703", "三安": "sh600703",
    "三花智控": "sz002050", "三花": "sz002050",
    "拓普集团": "sh601689",
    "德赛西威": "sz002920",
    "华阳集团": "sz002906",
    "德赛电池": "sz000049",
    "欣旺达": "sz300207",
    "亿纬锂能": "sz300014",
    "赣锋锂业": "sz002460",
    "天齐锂业": "sz002466",
    "华友钴业": "sh603799",
    "洛阳钼业": "sh603993",
    "紫金矿业": "sh601899",
    "江西铜业": "sh600362",
    "中国铝业": "sh601600",
    "宝钛股份": "sh600456",
    "西部超导": "sh688122",
    "科创50": "sh000688",
    "沪深300": "sh000300",
    "中证500": "sh000905",
    "中证1000": "sh000852",
    "创业板": "sz399006",
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "国证A股": "sz399317",
    "上证50": "sh000016",
    "沪深000001": "sh000001",
    "深证000001": "sz399001",
}


def _normalize(raw: str) -> Optional[str]:
    raw = raw.strip()
    if not raw:
        return None

    if raw.lower() in {k.lower() for k in _COMMON_STOCKS}:
        for k, v in _COMMON_STOCKS.items():
            if k.lower() == raw.lower():
                return v

    if raw.startswith(("sh.", "sz.", "bj.")):
        code = raw.split(".", 1)[1]
        prefix = raw[:2]
        return f"{prefix}{code}"

    pure = raw.lstrip("shzxbjSHZXBJ./- ")
    if pure.isdigit():
        code = pure
        if code.startswith(("4", "8")):
            return f"bj{code}"
        elif code.startswith("6") or code.startswith("5"):
            return f"sh{code}"
        else:
            return f"sz{code}"

    url = f"https://suggest3.sinajs.cn/suggest/type=11,12,13,14,15&key={raw}"
    headers = {"Referer": "https://finance.sina.com.cn"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        text = resp.text.strip()
        if text and "=" in text:
            content = text.split("=", 1)[1].strip().strip('";\n')
            if content:
                fields = content.split(",")
                if len(fields) >= 3:
                    code = fields[2].strip()
                    if code.startswith(("sh", "sz", "bj")):
                        return code
    except Exception:
        pass

    return None


def _kline_code(sina_code: str) -> str:
    return sina_code[2:]


def _fetch_kline_sina(sina_code: str, datalen: int = 300) -> pd.DataFrame:
    url = (
        f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
        f"/CN_MarketData.getKLineData?symbol={sina_code}&scale=240&ma=5&datalen={datalen}"
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
    return df


def _fetch_realtime_sina(sina_code: str) -> dict:
    url = f"https://hq.sinajs.cn/list={sina_code}"
    headers = {"Referer": "https://finance.sina.com.cn"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    text = resp.text.strip()
    if "=\"\"}" in text or "var hq_str" not in text:
        raise ValueError(f"未找到股票 {sina_code} 的实时数据")

    raw = text.split('"')[1]
    fields = raw.split(",")
    if len(fields) < 10:
        raise ValueError(f"股票 {sina_code} 数据格式异常")

    name = fields[0]
    current_price = float(fields[3]) if fields[3] else 0.0
    yesterday_close = float(fields[2]) if fields[2] else 0.0
    today_open = float(fields[1]) if fields[1] else 0.0
    today_high = float(fields[4]) if fields[4] else 0.0
    today_low = float(fields[5]) if fields[5] else 0.0
    date_str = fields[30] if len(fields) > 30 and fields[30].strip() else ""

    return {
        "name": name,
        "current_price": current_price,
        "yesterday_close": yesterday_close,
        "today_open": today_open,
        "today_high": today_high,
        "today_low": today_low,
        "date": date_str,
    }


def _calculate_macdv(close: pd.Series, high: pd.Series, low: pd.Series) -> pd.Series:
    if len(close) < 26:
        return pd.Series([0.0] * len(close), index=close.index)

    prev_close = close.shift(1)
    mytr = np.maximum(
        high - low,
        np.maximum((high - prev_close).abs(), (low - prev_close).abs())
    )
    atr26 = mytr.rolling(window=26, min_periods=1).mean()
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    diff = ema12 - ema26
    rawvalue = diff / atr26.replace(0, np.nan)
    macdv = np.where(atr26 > 0, rawvalue * 100, 0.0)
    return pd.Series(macdv, index=close.index)


def _calculate_rsi14(close: pd.Series) -> pd.Series:
    if len(close) < 14:
        return pd.Series([50.0] * len(close), index=close.index)

    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=14, min_periods=14).mean().copy()
    avg_loss = loss.rolling(window=14, min_periods=14).mean().copy()

    for i in range(14, len(gain)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * 13 + gain.iloc[i]) / 14
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * 13 + loss.iloc[i]) / 14

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = (100 - (100 / (1 + rs))).fillna(50.0)
    return rsi


def _get_macdv_trend(macdv: float) -> str:
    if macdv > 150:
        return "momentum_peak"
    elif macdv > 50:
        return "strong_up"
    elif macdv >= -50:
        return "oscillation"
    elif macdv >= -150:
        return "strong_down"
    else:
        return "momentum_decay"


def _get_rsi_signal(rsi: float) -> str:
    if rsi > 70:
        return "overbought"
    elif rsi < 30:
        return "oversold"
    return "neutral"


def _get_recommendation(macdv: float, rsi: float) -> str:
    if macdv < 50 and rsi > 70:
        return "右侧卖点"
    if macdv > 150 and rsi > 70:
        return "左侧卖点"
    if macdv < -150 and rsi < 30:
        return "左侧买点"
    if 50 <= macdv <= 150 and rsi < 30:
        return "右侧买点"
    return "观望"


def query_single_stock(code_or_name: str) -> dict:
    try:
        sina_code = _normalize(code_or_name)
        if not sina_code:
            raise ValueError(f"无法解析股票代码: {code_or_name}")

        df = _fetch_kline_sina(sina_code, datalen=300)
        if df.empty:
            raise ValueError(f"K线数据为空")
        if len(df) < 26:
            raise ValueError(f"数据不足（{len(df)}条），需要至少26条数据")

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)

        macdv_series = _calculate_macdv(close, high, low)
        rsi_series = _calculate_rsi14(close)

        latest_macdv = float(macdv_series.iloc[-1])
        latest_rsi = float(rsi_series.iloc[-1])

        rt = _fetch_realtime_sina(sina_code)
        trade_date = rt["date"] if rt["date"] else df["date"].max().strftime("%Y-%m-%d")
        current_price = rt["current_price"] if rt["current_price"] > 0 else float(df.iloc[-1]["close"])

        stock_code = sina_code[2:]
        stock_name = rt["name"] if rt["name"] else stock_code

        return {
            "stock_name": stock_name,
            "stock_code": stock_code,
            "trade_date": trade_date,
            "current_price": round(current_price, 2),
            "macdv": round(latest_macdv, 2),
            "rsi14": round(latest_rsi, 2),
            "macdv_trend": _get_macdv_trend(latest_macdv),
            "rsi14_signal": _get_rsi_signal(latest_rsi),
            "recommendation": _get_recommendation(latest_macdv, latest_rsi),
            "error": None,
        }

    except Exception as e:
        return {
            "stock_name": code_or_name.strip(),
            "stock_code": "",
            "trade_date": "",
            "current_price": 0.0,
            "macdv": 0.0,
            "rsi14": 0.0,
            "macdv_trend": "neutral",
            "rsi14_signal": "neutral",
            "recommendation": None,
            "error": str(e),
        }


def query_batch_stocks(queries: list[str]) -> dict:
    results = [query_single_stock(q) for q in queries]
    return {
        "results": results,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }