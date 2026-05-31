"""
定时任务调度器模块

本模块负责管理后台定时任务的调度与执行，主要包括：
1. 五年之锚数据每日更新任务
2. 红利之美数据每日更新任务

定时任务在应用启动时自动开始，在应用关闭时自动停止。
数据更新时间为每日收盘后（默认20:00），确保获取当日完整交易数据。
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from app.services.sina_service import sina_data_service
from app.services.hongli_service import hongli_data_service
from app.services.growth_value_service import gv_data_service
from app.services.cache_service import cache_service
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# 全局调度器实例，应用启动时初始化，关闭时销毁
scheduler: BackgroundScheduler | None = None


# =============================================================================
# 辅助函数
# =============================================================================

def _save_to_cache(index_code: str, df):
    """
    将DataFrame数据保存到缓存

    参数:
        index_code: 指数代码
        df: 包含历史数据的DataFrame，需包含列：date, open, high, low, close, volume

    数据处理逻辑:
        - 提取关键列（日期、开高低收、成交量）
        - 转换日期格式为YYYY-MM-DD
        - 添加默认字段（amount=0, adjustflag="1"）
        - 保存到缓存并更新最后更新时间
    """
    records = df[["date", "open", "high", "low", "close", "volume"]].copy()
    records["date"] = records["date"].dt.strftime("%Y-%m-%d")
    records["amount"] = 0.0
    records["adjustflag"] = "1"
    cache_service.save_stock_data(index_code, records.to_dict("records"))
    cache_service.set_last_update(
        index_code,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


# =============================================================================
# 定时任务定义
# =============================================================================

def update_anchor_data():
    """
    五年之锚数据更新任务

    触发时间: 每日 settings.data_update_hour:settings.data_update_minute（默认20:00）

    执行内容:
        1. 遍历主要指数列表：沪深300、上证指数、深圳成指
        2. 逐个从数据源获取最新历史数据
        3. 将数据保存到本地缓存
        4. 记录更新日志

    处理的指数:
        - sz.399317: 沪深300
        - sh.000001: 上证指数
        - sz.399001: 深圳成指

    错误处理:
        - 单个指数获取失败不影响其他指数
        - 失败时记录错误日志，继续处理下一个指数
    """
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
    """
    红利之美数据更新任务

    触发时间: 每日 settings.data_update_hour:settings.data_update_minute（默认20:00）

    执行内容:
        1. 遍历红利相关指数列表
        2. 逐个刷新数据（包含红利因子计算）
        3. 记录更新日志

    处理的指数:
        - sh515180: 中证红利指数
        - sz399317: 沪深300（用于对比）

    错误处理:
        - 单个指数获取失败不影响其他指数
        - 失败时记录错误日志，继续处理下一个指数
    """
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


def update_growth_value_data():
    """
    成长价值数据更新任务

    处理的指数:
        - sz159259: 成长100
        - sz159263: 价值100
    """
    try:
        logger.info(f"开始执行成长价值数据更新: {datetime.now()}")
        gv_codes = [
            ("sz159259", "sz159259"),
            ("sz159263", "sz159263"),
        ]
        for code, symbol in gv_codes:
            try:
                df = gv_data_service.refresh_data(code, symbol)
                logger.info(f"{code} 数据更新完成，共 {len(df)} 条")
            except Exception as e:
                logger.error(f"{code} 成长价值数据更新失败: {e}")
        logger.info("成长价值数据更新完成")
    except Exception as e:
        logger.error(f"成长价值定时任务失败: {e}")


# =============================================================================
# 调度器管理
# =============================================================================

def start_scheduler():
    """
    启动定时任务调度器

    执行逻辑:
        1. 创建BackgroundScheduler实例（后台运行，不阻塞主线程）
        2. 配置CronTrigger触发器，设定每日执行时间
        3. 注册两个定时任务：五年之锚更新、红利之美更新
        4. 启动调度器

    任务配置:
        - job_id: 唯一标识符
        - name: 任务显示名称
        - replace_existing: 如果已存在同名任务则替换

    注意:
        - 触发时间从配置文件读取（data_update_hour, data_update_minute）
        - 默认每日20:00执行，适配A股收盘时间
    """
    global scheduler
    try:
        if scheduler is None:
            scheduler = BackgroundScheduler()

        # 配置Cron触发器，每日固定时间执行
        trigger = CronTrigger(
            hour=settings.data_update_hour,
            minute=settings.data_update_minute
        )

        # 注册五年之锚数据更新任务
        scheduler.add_job(
            update_anchor_data,
            trigger=trigger,
            id="daily_anchor_update",
            name="五年之锚每日数据更新",
            replace_existing=True
        )

        # 注册红利之美数据更新任务
        scheduler.add_job(
            update_hongli_data,
            trigger=trigger,
            id="daily_hongli_update",
            name="红利之美每日数据更新",
            replace_existing=True
        )

        # 注册成长价值数据更新任务
        scheduler.add_job(
            update_growth_value_data,
            trigger=trigger,
            id="daily_growth_value_update",
            name="成长价值每日数据更新",
            replace_existing=True
        )

        scheduler.start()
        logger.info(f"定时任务已启动，每日 {settings.data_update_hour}:{settings.data_update_minute:02d} 执行")
    except Exception as e:
        logger.error(f"启动定时任务失败: {e}")


def shutdown_scheduler():
    """
    关闭定时任务调度器

    执行逻辑:
        1. 检查调度器是否存在
        2. 安全关闭调度器（等待正在执行的任务完成）
        3. 重置全局调度器实例为None

    使用场景:
        - 应用关闭时调用
        - 确保定时任务不会在应用关闭后继续运行
    """
    global scheduler
    try:
        if scheduler is not None:
            scheduler.shutdown()
            scheduler = None
            logger.info("定时任务已关闭")
    except Exception as e:
        logger.error(f"关闭定时任务失败: {e}")
