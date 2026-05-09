from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime
import time
import logging

from app.models.macdv_schemas import MacdvQueryResponse, MacdvStockItem, MacdvHealthResponse
from app.services.macdv_service import query_batch_stocks

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/macdv", tags=["趋势信号"])

_rate_limit_store: dict = {}
_rate_limit_window = 60
_rate_limit_max = 10


def _check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    window = [t for t in _rate_limit_store.get(client_ip, []) if now - t < _rate_limit_window]
    if len(window) >= _rate_limit_max:
        return False
    window.append(now)
    _rate_limit_store[client_ip] = window
    return True


@router.get("/health", response_model=MacdvHealthResponse)
async def health():
    return MacdvHealthResponse(status="ok", time=datetime.now().isoformat())


@router.post("/batch_query", response_model=MacdvQueryResponse)
async def batch_query(request: Request, queries: List[str]):
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")

    if not queries or not any(q.strip() for q in queries):
        raise HTTPException(status_code=422, detail="查询列表不能为空")

    queries = [q.strip() for q in queries if q.strip()]
    if not queries:
        raise HTTPException(status_code=422, detail="查询列表不能为空")

    try:
        result = query_batch_stocks(queries)
        return MacdvQueryResponse(**result)
    except Exception as e:
        logger.error(f"批量查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))