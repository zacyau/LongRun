"""
趋势信号模块 - MACD等技术指标批量查询

本模块提供股票/指数的技术指标批量查询功能，基于MACD等趋势
跟踪指标帮助用户判断市场状态（上涨/下跌/震荡）。

主要功能：
- 批量查询多只股票的技术指标
- 限流保护，防止API滥用
- 健康状态检查
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime
import time
import logging

from app.models.macdv_schemas import MacdvQueryResponse, MacdvStockItem, MacdvHealthResponse
from app.services.macdv_service import query_batch_stocks

logger = logging.getLogger(__name__)

# 路由前缀，API版本v1，标签为"趋势信号"
router = APIRouter(prefix="/api/v1/macdv", tags=["趋势信号"])

# -----------------------------------------------------------------------------
# 限流配置
# -----------------------------------------------------------------------------
# 限流存储：{客户端IP: [请求时间戳列表]}
_rate_limit_store: dict = {}

# 限流时间窗口（秒）
_rate_limit_window = 60

# 时间窗口内最大请求数
_rate_limit_max = 10


def _check_rate_limit(client_ip: str) -> bool:
    """
    检查客户端IP是否超过限流阈值

    限流策略：
    - 每个IP在60秒内最多允许10次请求
    - 超出限制返回False，请求将被拒绝

    参数:
        client_ip: 客户端IP地址

    返回:
        True: 请求允许
        False: 请求被限流拦截
    """
    now = time.time()
    # 筛选出在时间窗口内的请求时间戳
    window = [t for t in _rate_limit_store.get(client_ip, []) if now - t < _rate_limit_window]
    if len(window) >= _rate_limit_max:
        return False
    window.append(now)
    _rate_limit_store[client_ip] = window
    return True


# =============================================================================
# API 端点
# =============================================================================

@router.get("/health", response_model=MacdvHealthResponse)
async def health():
    """
    健康检查接口

    HTTP方法: GET
    路径: /api/v1/macdv/health

    功能说明:
        - 检查服务运行状态
        - 返回当前服务器时间

    响应内容 (MacdvHealthResponse):
        - status: 服务状态，"ok"表示正常
        - time: 当前服务器时间（ISO格式）
    """
    return MacdvHealthResponse(status="ok", time=datetime.now().isoformat())


@router.post("/batch_query", response_model=MacdvQueryResponse)
async def batch_query(request: Request, queries: List[str]):
    """
    批量查询股票/指数的技术指标

    HTTP方法: POST
    路径: /api/v1/macdv/batch_query

    功能说明:
        - 批量查询多只股票或指数的MACD等技术指标
        - 根据指标值判断当前趋势状态
        - 内置限流保护，防止滥用

    请求参数:
        queries (List[str]): 查询列表，包含股票或指数代码
            示例: ["sh600000", "sz000001", "sz.399317"]

    请求体格式:
        ["sh600000", "sz000001"]

    响应内容 (MacdvQueryResponse):
        - results: 查询结果列表
            - code: 股票/指数代码
            - name: 名称
            - macd: MACD指标值
            - signal: Signal线值
            - histogram: MACD柱状图值
            - trend: 趋势判断（"上涨"、"下跌"、"震荡"）
        - query_count: 本次查询的股票数量
        - generated_at: 结果生成时间

    错误响应:
        - 429: 请求过于频繁，触发限流
        - 422: 查询列表为空或无效
        - 500: 服务器内部错误
    """
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")

    # 验证查询列表是否为空
    if not queries or not any(q.strip() for q in queries):
        raise HTTPException(status_code=422, detail="查询列表不能为空")

    # 清理查询列表，去除空白字符
    queries = [q.strip() for q in queries if q.strip()]
    if not queries:
        raise HTTPException(status_code=422, detail="查询列表不能为空")

    try:
        result = query_batch_stocks(queries)
        return MacdvQueryResponse(**result)
    except Exception as e:
        logger.error(f"批量查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
