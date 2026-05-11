"""
红利之美模块 - 红利策略对比分析

本模块提供红利策略相关的数据查询服务，支持对不同红利指数
（如中证红利指数、沪深300等）进行对比分析，帮助用户理解
红利再投资与指数投资的收益差异。

主要功能：
- 获取多指数对比数据
- 健康状态检查
- 数据强制刷新
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
import logging

from app.services.hongli_service import get_all_data
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

# 路由前缀，API版本v1，标签为"红利之美"
router = APIRouter(prefix="/api/v1/hongli", tags=["红利之美"])


# =============================================================================
# API 端点
# =============================================================================

@router.get("/data")
async def get_compare_data(
    start_date: Optional[str] = Query(default=None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="结束日期 YYYY-MM-DD"),
):
    """
    获取红利对比数据

    HTTP方法: GET
    路径: /api/v1/hongli/data

    功能说明:
        - 获取中证红利指数与沪深300指数的对比数据
        - 计算不同时间周期下的收益对比
        - 支持按日期范围过滤数据

    请求参数:
        - start_date (str, 可选): 开始日期，格式YYYY-MM-DD
        - end_date (str, 可选): 结束日期，格式YYYY-MM-DD

    响应内容:
        - generated_at: 数据生成时间
        - compare_data: 对比数据列表，包含各指数在不同日期的净值、收益率等
        - summary: 对比摘要（总收益率、年化收益率等）

    错误响应:
        - 500: 服务器内部错误
    """
    try:
        data = get_all_data(start_date=start_date, end_date=end_date)
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取红利对比数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """
    健康检查接口

    HTTP方法: GET
    路径: /api/v1/hongli/health

    功能说明:
        - 检查服务运行状态
        - 获取各指数数据最后更新时间

    响应内容:
        - status: 服务状态，"ok"表示正常
        - time: 当前服务器时间（ISO格式）
        - last_update_hongli: 中证红利指数最后更新时间
        - last_update_guozheng: 沪深300最后更新时间
    """
    last_hongli = cache_service.get_last_update("sh515180")
    last_guozheng = cache_service.get_last_update("sz399317")
    return {
        "status": "ok",
        "time": datetime.now().isoformat(),
        "last_update_hongli": last_hongli,
        "last_update_guozheng": last_guozheng,
    }


@router.post("/refresh")
async def refresh_data():
    """
    手动刷新红利对比数据

    HTTP方法: POST
    路径: /api/v1/hongli/refresh

    功能说明:
        - 强制从数据源获取最新对比数据
        - 重新计算各指数收益对比
        - 更新缓存数据

    响应内容:
        - message: 操作结果信息
        - generated_at: 数据刷新后的生成时间

    错误响应:
        - 500: 服务器内部错误
    """
    try:
        data = get_all_data(force_refresh=True)
        return {
            "message": "数据刷新成功",
            "generated_at": data["generated_at"]
        }
    except Exception as e:
        logger.error(f"刷新红利数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
