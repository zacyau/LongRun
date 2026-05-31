"""
成长价值模块 - 成长/价值风格轮动分析

本模块提供成长100与价值100指数的对比分析服务，
帮助用户理解成长风格与价值风格的相对强弱和轮动节奏。

主要功能：
- 获取成长/价值对比数据
- 健康状态检查
- 数据强制刷新
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
import logging

from app.services.growth_value_service import get_all_data
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/growth-value", tags=["成长价值"])


@router.get("/data")
async def get_compare_data(
    start_date: Optional[str] = Query(default=None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="结束日期 YYYY-MM-DD"),
):
    try:
        data = get_all_data(start_date=start_date, end_date=end_date)
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取成长价值对比数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    last_growth = cache_service.get_last_update("sz159259")
    last_value = cache_service.get_last_update("sz159263")
    return {
        "status": "ok",
        "time": datetime.now().isoformat(),
        "last_update_growth": last_growth,
        "last_update_value": last_value,
    }


@router.post("/refresh")
async def refresh_data():
    try:
        data = get_all_data(force_refresh=True)
        return {
            "message": "数据刷新成功",
            "generated_at": data["generated_at"]
        }
    except Exception as e:
        logger.error(f"刷新成长价值数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
