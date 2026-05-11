"""
Long Run 应用主模块

这是FastAPI应用的入口点，负责：
1. 应用初始化配置
2. 中间件注册
3. 路由注册
4. 生命周期管理（启动/关闭事件）
5. 根路径处理

Long Run 应用包含两个主要功能模块：
- 五年之锚：指数数据追踪与支撑位分析
- 红利之美：红利策略收益对比分析
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.routers import anchor, hongli, macdv
from app.tasks.scheduler import start_scheduler, shutdown_scheduler

settings = get_settings()

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# 应用初始化
# =============================================================================

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,                        # API文档标题
    description="Long Run - 五年之锚 & 红利之美",     # API描述
    version="1.0.0",                                  # API版本
    debug=settings.debug                             # 调试模式
)

# -----------------------------------------------------------------------------
# 中间件配置
# -----------------------------------------------------------------------------

# 注册CORS中间件，允许跨域请求
# 配置说明：
# - allow_origins: 允许的来源域名列表
# - allow_credentials: 是否允许携带认证信息（cookies等）
# - allow_methods: 允许的HTTP方法，*表示全部允许
# - allow_headers: 允许的HTTP头，*表示全部允许
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# 路由注册
# =============================================================================

# 将各功能模块的路由注册到应用
# 路由前缀在各自的router定义中指定
app.include_router(anchor.router)   # 五年之锚相关API
app.include_router(hongli.router)   # 红利之美相关API
app.include_router(macdv.router)    # 趋势信号相关API


# =============================================================================
# 生命周期事件
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """
    应用启动事件处理

    执行时机: FastAPI应用启动时自动调用

    执行内容:
        1. 记录启动日志
        2. 启动定时任务调度器
        3. 记录启动完成日志

    定时任务说明:
        - 调度器启动后会按配置时间（默认每日20:00）自动执行数据更新任务
        - 任务包括：五年之锚数据更新、红利之美数据更新
    """
    logger.info("Long Run 应用启动中...")
    start_scheduler()
    logger.info("Long Run 应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件处理

    执行时机: FastAPI应用关闭时自动调用

    执行内容:
        1. 记录关闭日志
        2. 安全关闭定时任务调度器（等待正在执行的任务完成）
        3. 记录关闭完成日志
    """
    logger.info("Long Run 应用关闭中...")
    shutdown_scheduler()
    logger.info("Long Run 应用关闭完成")


# =============================================================================
# 根路径处理
# =============================================================================

@app.get("/")
async def root():
    """
    根路径处理

    HTTP方法: GET
    路径: /

    功能说明:
        - 返回API的基本信息
        - 提供版本号和可用模块列表
        - 指向API文档地址

    响应内容:
        - message: API描述信息
        - version: 当前API版本
        - modules: 已注册的功能模块列表
        - docs: API文档地址
    """
    return {
        "message": "Long Run API",
        "version": "1.0.0",
        "modules": ["五年之锚", "红利之美"],
        "docs": "/docs"
    }


# =============================================================================
# 应用启动入口
# =============================================================================

if __name__ == "__main__":
    """
    直接运行此文件时启动开发服务器

    使用uvicorn作为ASGI服务器，支持：
    - 热重载（debug模式下自动启用）
    - 配置监听地址和端口

    启动命令示例:
        python app/main.py
        或
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    """
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
