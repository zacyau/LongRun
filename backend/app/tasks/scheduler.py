from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from app.services.sina_service import sina_data_service
from app.services.hongli_service import hongli_data_service
from app.services.cache_service import cache_service
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

scheduler: BackgroundScheduler | None = None


def _save_to_cache(index_code: str, df):
    records = df[["date", "open", "high", "low", "close", "volume"]].copy()
    records["date"] = records["date"].dt.strftime("%Y-%m-%d")
    records["amount"] = 0.0
    records["adjustflag"] = "1"
    cache_service.save_stock_data(index_code, records.to_dict("records"))
    cache_service.set_last_update(
        index_code,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


def update_anchor_data():
    try:
        logger.info(f"开始执行五年之锚数据更新: {datetime.now()}")
        index_codes = ["sz.399317", "sh.000001", "sz.399001"]
        for code in index_codes:
            try:
                df = sina_data_service.fetch_history_data(code)
                if not df.empty:
                    _save_to_cache(code, df)
                    logger.info(f"{code} 数据更新完成，共 {len(df)} 条")
            except Exception as e:
                logger.error(f"{code} 数据更新失败: {e}")
        logger.info("五年之锚数据更新完成")
    except Exception as e:
        logger.error(f"五年之锚定时任务失败: {e}")


def update_hongli_data():
    try:
        logger.info(f"开始执行红利之美数据更新: {datetime.now()}")
        hongli_codes = [
            ("sh515180", "sh515180"),
            ("sz399317", "sz399317"),
        ]
        for code, symbol in hongli_codes:
            try:
                df = hongli_data_service.refresh_data(code, symbol)
                logger.info(f"{code} 数据更新完成，共 {len(df)} 条")
            except Exception as e:
                logger.error(f"{code} 红利数据更新失败: {e}")
        logger.info("红利之美数据更新完成")
    except Exception as e:
        logger.error(f"红利之美定时任务失败: {e}")


def start_scheduler():
    global scheduler
    try:
        if scheduler is None:
            scheduler = BackgroundScheduler()

        trigger = CronTrigger(
            hour=settings.data_update_hour,
            minute=settings.data_update_minute
        )

        scheduler.add_job(
            update_anchor_data,
            trigger=trigger,
            id="daily_anchor_update",
            name="五年之锚每日数据更新",
            replace_existing=True
        )

        scheduler.add_job(
            update_hongli_data,
            trigger=trigger,
            id="daily_hongli_update",
            name="红利之美每日数据更新",
            replace_existing=True
        )

        scheduler.start()
        logger.info(f"定时任务已启动，每日 {settings.data_update_hour}:{settings.data_update_minute:02d} 执行")
    except Exception as e:
        logger.error(f"启动定时任务失败: {e}")


def shutdown_scheduler():
    global scheduler
    try:
        if scheduler is not None:
            scheduler.shutdown()
            scheduler = None
            logger.info("定时任务已关闭")
    except Exception as e:
        logger.error(f"关闭定时任务失败: {e}")