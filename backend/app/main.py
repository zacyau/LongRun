from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.routers import anchor, hongli, macdv
from app.tasks.scheduler import start_scheduler, shutdown_scheduler

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Long Run - 五年之锚 & 红利之美",
    version="1.0.0",
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(anchor.router)
app.include_router(hongli.router)
app.include_router(macdv.router)


@app.on_event("startup")
async def startup_event():
    logger.info("Long Run 应用启动中...")
    start_scheduler()
    logger.info("Long Run 应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Long Run 应用关闭中...")
    shutdown_scheduler()
    logger.info("Long Run 应用关闭完成")


@app.get("/")
async def root():
    return {
        "message": "Long Run API",
        "version": "1.0.0",
        "modules": ["五年之锚", "红利之美"],
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )