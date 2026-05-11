"""
中证红利 vs 国证A股 对比分析服务模块

功能说明:
- 提供中证红利指数与国证A股指数的对比分析功能
- 计算两种指数的相对强弱关系、偏离度、RSI等指标
- 用于判断红利策略与市场平均的相对表现

数据源: 新浪财经 CN_MarketData.getKLineData API
缓存: SQLite (与五年之锚共享缓存服务)

核心分析指标:
1. 累计收益曲线 (Chart 1)
   - 将初始资金设为1000
   - 计算中证红利和国证A股的累计收益曲线
   - 用于比较两种策略的整体表现

2. 相对强弱比率 (Chart 2)
   - 比率 = 中证红利累计收益 / 国证A股累计收益
   - 计算242日移动平均线（均值）
   - 计算±2倍标准差通道（布林带）
   - %B指标：当前比率在通道中的位置
   - Bandwidth指标：通道宽度

3. 收益差分析 (Chart 3)
   - 40日累计收益差 = 中证红利40日收益 - 国证A股40日收益
   - 242日移动平均线（均值回归参考）
   - 用于捕捉短期相对强弱切换

4. RSI指标 (Chart 4)
   - 基于相对强弱比率计算的RSI14
   - 242日移动平均线
   - 用于判断相对强弱的超买超卖状态
"""
import math
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

# 指数配置表
# key: 内部使用的简称
# symbol: 新浪API使用的代码
# name: 显示名称
INDEX_CONFIGS = {
    "hongli": {"symbol": "sh515180", "name": "中证红利", "code": "sh515180"},
    "guozheng": {"symbol": "sz399317", "name": "国证A股", "code": "sz399317"},
}

# 请求数据的长度（默认2500条）
# 约10年的日线数据（每年约250个交易日）
HONGLI_DATALEN = 2500


def _raw_kline_to_df(rows: list) -> pd.DataFrame:
    """
    将缓存中的原始K线数据转换为DataFrame并计算收益

    参数说明:
        rows: 原始K线数据列表，每条记录包含date、open、high、low、close、volume

    返回值:
        pd.DataFrame，包含列：
        - date: 交易日期
        - close: 收盘价
        - return: 日收益率（小数形式）
        - total_return: 累计收益（初始值1000）
    """
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    # 计算日收益率
    df["return"] = df["close"].pct_change().fillna(0)
    # 计算累计收益（假设初始投资1000）
    df["total_return"] = (1 + df["return"]).cumprod() * 1000
    return df


def fetch_kline_sina(symbol: str, datalen: int = HONGLI_DATALEN) -> pd.DataFrame:
    """
    从新浪财经API获取K线数据

    参数说明:
        symbol: 新浪格式的股票代码，如"sh515180"
        datalen: 请求的数据条数，默认2500条（约10年日线数据）

    返回值:
        pd.DataFrame，包含列：date、open、close、high、low、volume、return、total_return

    API参数说明:
        - scale=240: 获取日K线数据
        - ma=5: 移动平均线参数（此处不实际使用）
    """
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
    # 计算日收益率
    df["return"] = df["close"].pct_change().fillna(0)
    # 计算累计收益
    df["total_return"] = (1 + df["return"]).cumprod() * 1000
    return df


class HongliDataService:
    """
    中证红利数据服务类

    提供中证红利和国证A股指数数据的获取和缓存管理功能
    支持智能缓存和强制刷新两种模式
    """

    def update_data(self, index_code: str, symbol: str) -> pd.DataFrame:
        """
        更新/获取指数数据（优先使用缓存）

        策略说明:
        1. 检查缓存是否有效（在TTL时间内更新过）
        2. 缓存有效时直接返回缓存数据
        3. 缓存无效时从新浪获取新数据并更新缓存

        参数说明:
            index_code: 指数代码（如"sh515180"）
            symbol: 新浪API使用的代码

        返回值:
            pd.DataFrame，包含K线数据和计算收益
        """
        # 检查缓存是否有效
        if cache_service.is_cache_valid(index_code):
            cached = cache_service.get_stock_data(index_code)
            if cached:
                logger.info(f"使用缓存数据: {index_code}")
                return _raw_kline_to_df(cached)

        # 缓存无效，从新浪获取数据
        logger.info(f"从新浪获取数据: {index_code} -> {symbol}")
        df = fetch_kline_sina(symbol)
        if df.empty:
            raise Exception(f"获取 {index_code} 数据为空")

        self._save_to_cache(index_code, df)
        return df

    def refresh_data(self, index_code: str, symbol: str) -> pd.DataFrame:
        """
        强制刷新数据（跳过缓存，直接从API获取）

        参数说明:
            index_code: 指数代码
            symbol: 新浪API使用的代码

        返回值:
            pd.DataFrame，包含K线数据和计算收益
        """
        logger.info(f"强制刷新: {index_code}")
        df = fetch_kline_sina(symbol)
        if df.empty:
            raise Exception(f"获取 {index_code} 数据为空")

        self._save_to_cache(index_code, df)
        return df

    def _save_to_cache(self, index_code: str, df: pd.DataFrame):
        """
        保存数据到缓存

        参数说明:
            index_code: 指数代码
            df: K线数据DataFrame

        实现说明:
            - 转换日期格式为字符串
            - 添加默认的amount和adjustflag字段
            - 批量写入数据库
        """
        records = df[["date", "open", "high", "low", "close", "volume"]].copy()
        records["date"] = records["date"].dt.strftime("%Y-%m-%d")
        records["amount"] = 0.0
        records["adjustflag"] = "1"
        cache_service.save_stock_data(index_code, records.to_dict("records"))
        cache_service.set_last_update(
            index_code,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        logger.info(f"{index_code} 缓存写入完成，共 {len(records)} 条")


hongli_data_service = HongliDataService()


def _slice_by_date(series: list, dates: list, start: Optional[str], end: Optional[str]) -> tuple:
    """
    按日期范围截取数据

    参数说明:
        series: 数据序列
        dates: 日期序列（与series对应）
        start: 开始日期（可选）
        end: 结束日期（可选）

    返回值:
        tuple: (截取后的日期列表, 截取后的数据列表)

    实现说明:
        - 二分查找开始和结束位置
        - 如果start晚于end，返回空列表
    """
    if not dates:
        return [], []
    start_idx = 0
    end_idx = len(dates) - 1
    if start:
        # 找到第一个 >= start 的位置
        for i, d in enumerate(dates):
            if d >= start:
                start_idx = i
                break
    if end:
        # 找到最后一个 <= end 的位置
        for i in range(len(dates) - 1, -1, -1):
            if dates[i] <= end:
                end_idx = i
                break
    if start_idx > end_idx:
        return [], []
    return dates[start_idx:end_idx + 1], series[start_idx:end_idx + 1]


def get_all_data(start_date: Optional[str] = None, end_date: Optional[str] = None,
                 force_refresh: bool = False) -> dict:
    """
    获取并计算中证红利与国证A股的对比分析数据

    参数说明:
        start_date: 可选，开始日期，格式"YYYY-MM-DD"
        end_date: 可选，结束日期，格式"YYYY-MM-DD"
        force_refresh: 是否强制刷新缓存，默认False

    返回值:
        dict，包含4个图表的数据：

    Chart 1 - 累计收益曲线:
        - dates: 日期列表
        - hongli: 中证红利累计收益
        - guozheng: 国证A股累计收益

    Chart 2 - 相对强弱比率:
        - dates: 日期列表
        - ratio: 比率（中证红利/国证A股）
        - ma242: 242日移动平均
        - upper: 上轨（均值+2倍标准差）
        - lower: 下轨（均值-2倍标准差）
        - pctB: %B指标（当前比率在通道中的位置）
        - bandwidth: 通道宽度百分比

    Chart 3 - 收益差分析:
        - dates: 日期列表
        - diff: 40日累计收益差
        - diff_ma242: 242日移动平均
        - mean: 平均收益差

    Chart 4 - RSI指标:
        - dates: 日期列表
        - rsi: RSI14
        - rsi_ma242: RSI的242日移动平均
        - latest_rsi: 最新RSI值
        - latest_rsi_ma: 最新RSI移动平均

    计算流程:
    1. 获取两个指数的数据
    2. 计算各自的累计收益
    3. 计算相对强弱比率及其布林带
    4. 计算40日累计收益差
    5. 计算RSI指标
    6. 按日期范围截取数据
    """
    dfs = {}

    # 1. 获取两个指数的数据
    for key, config in INDEX_CONFIGS.items():
        if force_refresh:
            df = hongli_data_service.refresh_data(config["code"], config["symbol"])
        else:
            df = hongli_data_service.update_data(config["code"], config["symbol"])
        if df.empty:
            raise Exception(f"获取 {config['name']} 数据失败")
        dfs[key] = df

    # 2. 准备数据
    hongli = dfs["hongli"][["date", "close", "return", "total_return"]].copy()
    guozheng = dfs["guozheng"][["date", "close", "return", "total_return"]].copy()
    # 重命名列以便合并
    guozheng.columns = ["date", "guozheng_close", "guozheng_return", "guozheng_tr"]
    hongli.columns = ["date", "hongli_close", "hongli_return", "hongli_tr"]

    # 按日期合并两个数据集（内连接，只保留共同日期）
    merged = hongli.merge(guozheng, on="date", how="inner")

    # 清理数据中的NaN值
    def clean(v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        return v

    def clean_list(lst):
        return [clean(x) for x in lst]

    # Chart 1数据：累计收益曲线
    chart1_dates_full = merged["date"].dt.strftime("%Y-%m-%d").tolist()
    chart1_hongli_full = clean_list(merged["hongli_tr"].round(4).tolist())
    chart1_guozheng_full = clean_list(merged["guozheng_tr"].round(4).tolist())

    # 3. 计算相对强弱比率及布林带
    merged["ratio"] = merged["hongli_tr"] / merged["guozheng_tr"]
    window = 242  # 约一年的交易日数
    merged["ratio_ma"] = merged["ratio"].rolling(window=window, min_periods=1).mean()
    merged["ratio_std"] = merged["ratio"].rolling(window=window, min_periods=1).std()
    merged["upper"] = merged["ratio_ma"] + 2 * merged["ratio_std"]  # 上轨
    merged["lower"] = merged["ratio_ma"] - 2 * merged["ratio_std"]  # 下轨

    # 计算%B和Bandwidth
    latest_full = merged.iloc[-1]
    upper_val = latest_full["upper"]
    lower_val = latest_full["lower"]
    ma_val = latest_full["ratio_ma"]
    ratio_val = latest_full["ratio"]
    # %B = (ratio - lower) / (upper - lower)，0表示在下轨，1表示在上轨
    pct_b = (ratio_val - lower_val) / (upper_val - lower_val) if upper_val != lower_val else 0.5
    # Bandwidth = (upper - lower) / ma * 100，表示通道宽度
    bandwidth = (upper_val - lower_val) / ma_val * 100 if ma_val != 0 else 0

    # Chart 2数据：相对强弱比率
    chart2_dates_full = chart1_dates_full
    chart2_ratio_full = clean_list(merged["ratio"].round(4).tolist())
    chart2_ma242_full = clean_list(merged["ratio_ma"].round(4).tolist())
    chart2_upper_full = clean_list(merged["upper"].round(4).tolist())
    chart2_lower_full = clean_list(merged["lower"].round(4).tolist())

    # 4. 计算40日累计收益差
    merged["hongli_40d"] = merged["hongli_return"].rolling(window=40, min_periods=1).sum()
    merged["guozheng_40d"] = merged["guozheng_return"].rolling(window=40, min_periods=1).sum()
    merged["profit_diff"] = merged["hongli_40d"] - merged["guozheng_40d"]
    merged["profit_diff_ma242"] = merged["profit_diff"].rolling(window=242, min_periods=1).mean()
    mean_diff = float(merged["profit_diff"].mean())

    # Chart 3数据：收益差
    chart3_dates_full = chart1_dates_full
    chart3_diff_full = clean_list((merged["profit_diff"] * 100).round(4).tolist())
    chart3_diff_ma242_full = clean_list((merged["profit_diff_ma242"] * 100).round(4).tolist())

    # 5. 计算RSI指标（基于比率）
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

    # Chart 4数据：RSI
    chart4_dates_full = chart1_dates_full
    chart4_rsi_full = clean_list(merged["rsi14"].round(4).tolist())
    chart4_rsi_ma242_full = clean_list(merged["rsi_ma242"].round(4).tolist())

    # 6. 按日期范围截取数据
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

    # 7. 计算截取数据的%BSlice
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

    # 8. 返回结果
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
