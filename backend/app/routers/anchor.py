"""
五年之锚模块 - 指数数据查询与展示

本模块提供大盘指数（如沪深300、国证1000等）的历史数据查询、
技术指标计算、以及数据刷新等功能。主要服务于"五年之锚"投资策略，
帮助用户追踪市场整体走势和计算关键支撑位。
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import asyncio
import logging

from app.models.schemas import ChartDataResponse, HealthResponse
from app.services.sina_service import sina_data_service
from app.services.indicator_service import indicator_service
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

# 路由前缀，API版本v1，标签为"五年之锚"
router = APIRouter(prefix="/api/v1/anchor", tags=["五年之锚"])

# 默认指数代码：沪深300（sz.399317）
DEFAULT_INDEX_CODE = "sz.399317"

# 数据获取超时时间（秒）
_FETCH_TIMEOUT = 30


# =============================================================================
# API 端点
# =============================================================================

@router.get("/data", response_model=ChartDataResponse)
async def get_chart_data(
    index_code: str = Query(default=DEFAULT_INDEX_CODE, description="指数代码"),
    start_date: Optional[str] = Query(default=None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="结束日期 YYYY-MM-DD")
):
    """
    获取指定指数的图表数据

    HTTP方法: GET
    路径: /api/v1/anchor/data

    功能说明:
        - 根据指数代码获取对应指数的历史K线数据
        - 计算技术指标（如均线、支撑位等）
        - 支持按日期范围过滤数据

    请求参数:
        - index_code (str, 可选): 指数代码，默认为"sz.399317"（沪深300）
          支持的代码示例：
          - sz.399317: 沪深300
          - sh.000001: 上证指数
          - sz.399001: 深圳成指
        - start_date (str, 可选): 开始日期，格式YYYY-MM-DD
        - end_date (str, 可选): 结束日期，格式YYYY-MM-DD

    响应内容 (ChartDataResponse):
        - dates: 日期列表
        - close_prices: 收盘价列表
        - highs: 最高价列表
        - lows: 最低价列表
        - volumes: 成交量列表
        - indicators: 技术指标数据（均线、支撑位等）

    错误响应:
        - 404: 未获取到数据或指定日期范围内无数据
        - 504: 数据获取超时
        - 500: 服务器内部错误
    """
    try:
        # 使用异步线程获取数据，设置超时保护
        df = await asyncio.wait_for(
            asyncio.to_thread(sina_data_service.update_data, index_code),
            timeout=_FETCH_TIMEOUT
        )

        if df.empty:
            raise HTTPException(status_code=404, detail="未获取到数据")

        # 通过指标服务准备图表数据（计算均线、支撑位等）
        chart_data = indicator_service.prepare_chart_data(df)

        # 按开始日期过滤数据
        if start_date:
            start_idx = next((i for i, d in enumerate(chart_data['dates']) if d >= start_date), None)
            if start_idx is not None:
                chart_data = {k: v[start_idx:] if isinstance(v, list) else v
                              for k, v in chart_data.items()}
            else:
                # 开始日期之后的范围内无数据，返回空
                chart_data = {k: ([] if isinstance(v, list) else None) for k, v in chart_data.items()}

        # 按结束日期过滤数据
        if end_date:
            end_idx = next((i for i, d in enumerate(chart_data['dates']) if d > end_date), None)
            if end_idx is not None:
                chart_data = {k: v[:end_idx] if isinstance(v, list) else v
                              for k, v in chart_data.items()}

        # 检查过滤后是否有数据
        if not chart_data['dates']:
            raise HTTPException(status_code=404, detail="指定日期范围内无数据")

        return ChartDataResponse(**chart_data)

    except asyncio.TimeoutError:
        logger.error("获取图表数据超时")
        raise HTTPException(status_code=504, detail="数据获取超时，请稍后重试")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取图表数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查接口

    HTTP方法: GET
    路径: /api/v1/anchor/health

    功能说明:
        - 检查服务运行状态
        - 获取指数数据最后更新时间

    响应内容 (HealthResponse):
        - status: 服务状态，"ok"表示正常，"error"表示异常
        - last_update: 最后更新时间，格式YYYY-MM-DD HH:MM:SS
        - message: 状态描述信息
    """
    try:
        last_update = cache_service.get_last_update(DEFAULT_INDEX_CODE)
        return HealthResponse(
            status="ok",
            last_update=last_update,
            message="服务运行正常"
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            last_update=None,
            message=f"服务异常: {str(e)}"
        )


@router.post("/refresh")
async def refresh_data(index_code: str = DEFAULT_INDEX_CODE):
    """
    手动刷新指数数据

    HTTP方法: POST
    路径: /api/v1/anchor/refresh

    功能说明:
        - 强制从数据源获取最新历史数据
        - 更新本地缓存中的指数数据
        - 更新最后更新时间戳

    请求参数:
        - index_code (str, 可选): 指数代码，默认为"sz.399317"（沪深300）

    响应内容:
        - message: 操作结果信息
        - records_count: 获取的记录数量
        - date_range: 数据日期范围
          - start: 数据起始日期
          - end: 数据结束日期

    错误响应:
        - 404: 未获取到数据
        - 504: 数据刷新超时
        - 500: 服务器内部错误
    """
    try:
        # 使用异步线程获取历史数据
        df = await asyncio.wait_for(
            asyncio.to_thread(sina_data_service.fetch_history_data, index_code),
            timeout=_FETCH_TIMEOUT
        )

        if df.empty:
            raise HTTPException(status_code=404, detail="未获取到数据")

        # 将数据转换为字典并保存到缓存
        records = df.to_dict('records')
        cache_service.save_stock_data(index_code, records)
        cache_service.set_last_update(
            index_code,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return {
            "message": "数据刷新成功",
            "records_count": len(records),
            "date_range": {
                "start": df['date'].min().strftime("%Y-%m-%d"),
                "end": df['date'].max().strftime("%Y-%m-%d")
            }
        }

    except asyncio.TimeoutError:
        logger.error("刷新数据超时")
        raise HTTPException(status_code=504, detail="数据刷新超时，请稍后重试")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"刷新数据失败: {str(e)}")
