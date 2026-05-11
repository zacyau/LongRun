"""
SQLite缓存服务模块

功能说明:
- 提供基于SQLite的本地数据缓存功能
- 用于存储股票/指数的历史K线数据，避免频繁请求外部API
- 支持缓存有效期管理（TTL）

数据库说明:
- 数据库文件路径: settings.database_url（配置中指定）
- 使用WAL模式提高并发性能
- 使用busy_timeout避免锁竞争

表结构:
1. stock_data: 存储K线数据
   - index_code: 指数代码（如"sz399317"）
   - date: 交易日期
   - open/high/low/close: 价格数据
   - volume: 成交量
   - amount: 成交额
   - adjustflag: 复权标志

2. cache_meta: 存储缓存元数据
   - key: 缓存键（如"last_update_sz399317"）
   - value: 缓存值（如更新时间）
   - updated_at: 最后更新时间
"""
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from app.config import get_settings

settings = get_settings()
DB_PATH = settings.database_url.replace("sqlite:///", "")


class CacheService:
    """
    SQLite缓存服务类

    提供股票数据的本地缓存功能，包括数据的读取、写入、有效期管理
    使用单例模式确保全局只有一个缓存服务实例
    """

    def __init__(self):
        """初始化缓存服务，创建数据库表（如不存在）"""
        self._init_db()
    
    def _init_db(self):
        """
        初始化数据库

        操作步骤:
        1. 确保数据库目录存在
        2. 创建数据库连接
        3. 设置SQLite性能参数（WAL模式、超时、同步级别）
        4. 创建数据表和索引（如不存在）
        """
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        # WAL模式：写操作不阻塞读操作，提高并发性能
        conn.execute("PRAGMA journal_mode=WAL")
        # 设置busy_timeout：等待锁释放的最大时间（毫秒）
        conn.execute("PRAGMA busy_timeout=5000")
        # NORMAL同步级别：平衡性能和数据安全
        conn.execute("PRAGMA synchronous=NORMAL")
        cursor = conn.cursor()

        # 创建K线数据表
        # UNIQUE(index_code, date) 确保每个指数每天只有一条记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_code TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                amount REAL,
                adjustflag TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(index_code, date)
            )
        """)

        # 创建缓存元数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_meta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引加速查询
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stock_data_code_date
            ON stock_data(index_code, date)
        """)

        conn.commit()
        conn.close()
    
    def get_last_update(self, index_code: str) -> Optional[str]:
        """
        获取指定指数的最后更新时间

        参数说明:
            index_code: 指数代码，如"sz399317"

        返回值:
            最后更新时间字符串，格式"YYYY-MM-DD HH:MM:SS"
            如果不存在返回None
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT updated_at FROM cache_meta WHERE key = ?",
            (f"last_update_{index_code}",)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def set_last_update(self, index_code: str, update_time: str):
        """
        设置指定指数的最后更新时间

        参数说明:
            index_code: 指数代码
            update_time: 更新时间，格式"YYYY-MM-DD HH:MM:SS"

        实现说明:
            使用INSERT OR REPLACE语义，当key已存在时更新value和updated_at
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO cache_meta (key, value, updated_at) 
               VALUES (?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET 
               value = excluded.value, updated_at = excluded.updated_at""",
            (f"last_update_{index_code}", update_time, update_time)
        )
        conn.commit()
        conn.close()
    
    def save_stock_data(self, index_code: str, data: List[Dict[str, Any]]):
        """
        保存股票K线数据到缓存

        参数说明:
            index_code: 指数代码
            data: K线数据列表，每条记录包含date、open、high、low、close、volume等字段

        实现说明:
            使用INSERT OR REPLACE语义，当index_code和date组合已存在时更新数据
            转换Timestamp对象为字符串格式存储
        """
        if not data:
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for row in data:
            # 将Timestamp对象转换为字符串
            date_val = row.get("date")
            if hasattr(date_val, 'strftime'):
                date_val = date_val.strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT INTO stock_data 
                (index_code, date, open, high, low, close, volume, amount, adjustflag)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(index_code, date) DO UPDATE SET
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                volume = excluded.volume,
                amount = excluded.amount,
                adjustflag = excluded.adjustflag
            """, (
                index_code,
                date_val,
                row.get("open"),
                row.get("high"),
                row.get("low"),
                row.get("close"),
                row.get("volume"),
                row.get("amount"),
                row.get("adjustflag")
            ))
        
        conn.commit()
        conn.close()
    
    def get_stock_data(self, index_code: str, start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取缓存的股票K线数据

        参数说明:
            index_code: 指数代码
            start_date: 可选，开始日期（格式"YYYY-MM-DD"）
            end_date: 可选，结束日期（格式"YYYY-MM-DD"）

        返回值:
            K线数据列表，每条记录是一个字典
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 构建查询语句
        query = "SELECT * FROM stock_data WHERE index_code = ?"
        params = [index_code]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        # 按日期升序排列
        query += " ORDER BY date ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def is_cache_valid(self, index_code: str) -> bool:
        """
        检查缓存是否有效

        判断依据:
            缓存有效需要满足以下条件：
            1. 存在最后更新时间记录
            2. 当前时间距离最后更新时间在TTL（缓存生存时间）范围内

        参数说明:
            index_code: 指数代码

        返回值:
            True表示缓存有效，False表示缓存无效或过期
        """
        last_update = self.get_last_update(index_code)
        if not last_update:
            return False
        
        try:
            # 解析最后更新时间
            last_dt = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
            # 获取配置的TTL（小时）
            ttl = timedelta(hours=settings.cache_ttl_hours)
            # 判断是否在TTL范围内
            return datetime.now() - last_dt < ttl
        except:
            return False
    
    def get_date_range(self, index_code: str) -> tuple:
        """
        获取缓存数据的日期范围

        参数说明:
            index_code: 指数代码

        返回值:
            tuple: (最早日期, 最晚日期)
            如果没有数据返回(None, None)
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MIN(date), MAX(date) FROM stock_data WHERE index_code = ?",
            (index_code,)
        )
        result = cursor.fetchone()
        conn.close()
        return result if result else (None, None)


cache_service = CacheService()
