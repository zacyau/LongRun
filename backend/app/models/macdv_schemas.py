from pydantic import BaseModel
from typing import Optional, List


class MacdvStockItem(BaseModel):
    stock_name: str
    stock_code: str
    trade_date: str
    current_price: float
    macdv: float
    rsi14: float
    macdv_trend: str
    rsi14_signal: str
    status_description: Optional[str] = None
    error: Optional[str] = None


class MacdvQueryResponse(BaseModel):
    results: List[MacdvStockItem]
    updated_at: str


class MacdvHealthResponse(BaseModel):
    status: str
    time: str