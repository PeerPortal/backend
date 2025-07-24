"""
启航引路人后端主应用
FastAPI 应用的主入口点，包含应用配置、中间件和路由注册
"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.db import lifespan, check_db_health
from app.api.routers import auth_router, user_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,  # 使用生命周期管理器
    docs_url="/docs" if settings.DEBUG else None,  # 生产环境可关闭文档
    redoc_url="/redoc" if settings.DEBUG else None,
)


# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# 添加可信主机中间件（生产环境安全）
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_ORIGINS
    )


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器：捕获所有未处理的异常，记录日志并返回500错误
    """
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "服务器内部错误，请稍后重试",
            "error_id": str(id(exc))  # 用于错误追踪
        },
    )


# 404 处理器
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 错误处理器"""
    return JSONResponse(
        status_code=404,
        content={"detail": f"请求的路径 {request.url.path} 不存在"}
    )


# 健康检查端点
@app.get(
    "/health",
    summary="健康检查",
    description="检查应用和数据库连接状态",
    tags=["Health"]
)
async def health_check():
    """
    健康检查端点
    检查应用状态和数据库连接
    """
    try:
        db_healthy = await check_db_health()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "version": settings.VERSION,
            "debug": settings.DEBUG
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "error",
                "error": str(e)
            }
        )


# 根路径
@app.get(
    "/",
    summary="API 根路径",
    description="返回 API 基本信息"
)
async def root():
    """API 根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "docs_url": "/docs" if settings.DEBUG else "文档已在生产环境中禁用",
        "health_check": "/health"
    }


# 注册 API 路由
app.include_router(
    auth_router.router,
    prefix="/api/v1/auth",
    tags=["认证"]
)

app.include_router(
    user_router.router,
    prefix="/api/v1/users",
    tags=["用户"]
)


# 中间件：请求日志记录
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"收到请求: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # 记录响应信息
    process_time = time.time() - start_time
    logger.info(
        f"请求处理完成: {request.method} {request.url} - "
        f"状态码: {response.status_code} - 耗时: {process_time:.4f}s"
    )
    
    return response


# 启动事件处理器
@app.on_event("startup")
async def startup_event():
    """应用启动时的事件处理"""
    logger.info(f"🚀 {settings.APP_NAME} v{settings.VERSION} 正在启动...")
    logger.info(f"🔧 调试模式: {'开启' if settings.DEBUG else '关闭'}")
    logger.info(f"🌐 服务器地址: http://{settings.HOST}:{settings.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的事件处理"""
    logger.info(f"🔄 {settings.APP_NAME} 正在关闭...")


# 导入缺失的模块
import time


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    ) 