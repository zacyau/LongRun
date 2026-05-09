import pandas as pd
import numpy as np
import requests
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


SINA_INDEX_MAP = {
    "sz.399317": "sz399317",
    "sh.000001": "sh000001",
    "sz.399001": "sz399001",
    "sh.000300": "sh000300",
}


def fetch_kline_sina(symbol: str, datalen: int = 5000) -> pd.DataFrame:
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
    return df


class SinaDataService:
    def fetch_history_data(
        self,
        index_code: str = "sz.399317",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        sina_symbol = SINA_INDEX_MAP.get(index_code, "sz399317")
        logger.info(f"从新浪获取数据: {index_code} -> {sina_symbol}")

        df = fetch_kline_sina(sina_symbol)
        if df.empty:
            raise ValueError(f"获取 {index_code} 数据为空")

        if start_date:
            df = df[df['date'] >= pd.to_datetime(start_date)].reset_index(drop=True)
        if end_date:
            df = df[df['date'] <= pd.to_datetime(end_date)].reset_index(drop=True)

        logger.info(f"获取到 {len(df)} 条数据")
        return df

    def update_data(self, index_code: str = "sz.399317") -> pd.DataFrame:
        if cache_service.is_cache_valid(index_code):
            logger.info("使用缓存数据")
            cached_data = cache_service.get_stock_data(index_code)
            if cached_data:
                df = pd.DataFrame(cached_data)
                df['date'] = pd.to_datetime(df['date'])
                return df

        logger.info(f"从新浪获取 {index_code} 数据")
        df = self.fetch_history_data(index_code)

        if not df.empty:
            records = df.to_dict('records')
            cache_service.save_stock_data(index_code, records)
            cache_service.set_last_update(
                index_code,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

        return df


sina_data_service = SinaDataService()
