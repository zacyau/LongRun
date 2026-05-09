from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
import logging

from app.services.hongli_service import get_all_data
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/hongli", tags=["红利之美"])


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
        logger.error(f"获取红利对比数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
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
    try:
        data = get_all_data(force_refresh=True)
        return {
            "message": "数据刷新成功",
            "generated_at": data["generated_at"]
        }
    except Exception as e:
        logger.error(f"刷新红利数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))