"""
新浪财经数据服务模块

功能说明:
- 提供从新浪财经API获取股票/指数历史K线数据的功能
- 支持从缓存读取数据，避免频繁请求外部API
- 主要用于获取上证指数、深证成指、沪深300、国证A股等大盘指数数据

数据来源: 新浪财经 CN_MarketData.getKLineData API
缓存机制: 使用SQLite本地缓存，通过cache_service实现
数据周期: 日线数据（scale=240表示240分钟，即日K线）
"""

import pandas as pd
import numpy as np
import requests
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

# 指数代码映射表：从标准代码格式（如"sz.399317"）转换为新浪格式（如"sz399317"）
# 新浪API使用的格式是"sh000001"而非"sh.000001"
SINA_INDEX_MAP = {
    "sz.399317": "sz399317",  # 国证A股
    "sh.000001": "sh000001",  # 上证指数
    "sz.399001": "sz399001",  # 深证成指
    "sh.000300": "sh000300",  # 沪深300
}


def fetch_kline_sina(symbol: str, datalen: int = 5000) -> pd.DataFrame:
    """
    从新浪财经API获取K线数据

    参数说明:
        symbol: 新浪格式的股票代码，如"sz399317"、"sh000001"
        datalen: 请求的数据条数，默认5000条（约20年日线数据）

    返回值:
        pd.DataFrame，包含列：date（日期）、open（开盘价）、close（收盘价）、
        high（最高价）、low（最低价）、volume（成交量）

    API说明:
        - scale=240: 表示获取日K线数据（240分钟=一个交易日）
        - ma=5: 移动平均线参数，此处不实际使用（数据中已包含基本价格）
    """
    # 构建新浪财经K线数据API URL
    # 格式: https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData
    url = (
        f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
        f"/CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=5&datalen={datalen}"
    )
    resp = requests.get(url, timeout=15)  # 15秒超时
    resp.raise_for_status()  # HTTP错误时抛出异常
    data = resp.json()

    # 新浪API返回空数据时返回空DataFrame
    if not data:
        return pd.DataFrame()

    # 将JSON数据转换为DataFrame记录格式
    # 新浪返回的数据结构: [{"day": "2024-01-01", "open": "3000.0", "close": "3010.0", ...}, ...]
    records = []
    for line in data:
        records.append({
            "date": line["day"],      # 日期字符串，格式如"2024-01-01"
            "open": float(line["open"]),   # 开盘价
            "close": float(line["close"]), # 收盘价
            "high": float(line["high"]),    # 最高价
            "low": float(line["low"]),      # 最低价
            "volume": float(line["volume"]), # 成交量
        })

    df = pd.DataFrame(records)
    # 转换日期列为datetime类型，便于后续日期过滤和排序
    df["date"] = pd.to_datetime(df["date"])
    # 按日期升序排列，确保数据时间顺序正确
    df = df.sort_values("date").reset_index(drop=True)
    return df


class SinaDataService:
    """
    新浪数据服务类

    提供指数历史数据的获取和缓存管理功能
    支持按日期范围过滤数据
    """

    def fetch_history_data(
        self,
        index_code: str = "sz.399317",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        获取指数历史数据（直接从新浪API获取，不使用缓存）

        参数说明:
            index_code: 标准格式的指数代码，如"sz.399317"（国证A股）
            start_date: 可选，开始日期，格式"YYYY-MM-DD"
            end_date: 可选，结束日期，格式"YYYY-MM-DD"

        返回值:
            pd.DataFrame，包含指定日期范围的K线数据

        代码转换逻辑:
            1. 通过SINA_INDEX_MAP将标准代码转为新浪格式
            2. 如未找到映射，默认使用"sz399317"（国证A股）
        """
        # 将标准格式代码转换为新浪格式
        # 例如: "sz.399317" -> "sz399317"
        sina_symbol = SINA_INDEX_MAP.get(index_code, "sz399317")
        logger.info(f"从新浪获取数据: {index_code} -> {sina_symbol}")

        # 调用API获取K线数据
        df = fetch_kline_sina(sina_symbol)
        if df.empty:
            raise ValueError(f"获取 {index_code} 数据为空")

        # 按日期范围过滤数据（如果指定了日期）
        if start_date:
            # 过滤掉start_date之前的数据
            df = df[df['date'] >= pd.to_datetime(start_date)].reset_index(drop=True)
        if end_date:
            # 过滤掉end_date之后的数据
            df = df[df['date'] <= pd.to_datetime(end_date)].reset_index(drop=True)

        logger.info(f"获取到 {len(df)} 条数据")
        return df

    def update_data(self, index_code: str = "sz.399317") -> pd.DataFrame:
        """
        更新/获取指数数据（优先使用缓存）

        策略说明:
            1. 首先检查缓存是否有效（通过cache_ttl_hours配置）
            2. 缓存有效时直接返回缓存数据，避免重复请求API
            3. 缓存无效或不存在时，从新浪获取新数据并更新缓存

        参数说明:
            index_code: 标准格式的指数代码

        返回值:
            pd.DataFrame，包含K线数据
        """
        # 检查缓存是否有效（是否在TTL时间内更新过）
        if cache_service.is_cache_valid(index_code):
            logger.info("使用缓存数据")
            cached_data = cache_service.get_stock_data(index_code)
            if cached_data:
                # 将缓存数据转换为DataFrame并确保日期格式正确
                df = pd.DataFrame(cached_data)
                df['date'] = pd.to_datetime(df['date'])
                return df

        # 缓存无效，从新浪获取数据
        logger.info(f"从新浪获取 {index_code} 数据")
        df = self.fetch_history_data(index_code)

        if not df.empty:
            # 将新数据保存到缓存
            records = df.to_dict('records')
            cache_service.save_stock_data(index_code, records)
            # 记录本次更新时间，用于判断缓存有效性
            cache_service.set_last_update(
                index_code,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

        return df


# 单例模式：全局共享的新浪数据服务实例
sina_data_service = SinaDataService()
