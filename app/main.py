"""
启航引路人后端主应用
FastAPI 应用的主入口点，包含应用配置、中间件和路由注册
"""
# 首先加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # 如果没有安装python-dotenv，继续使用系统环境变量

import logging
import time
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.db import lifespan, check_db_health

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# 创建留学双边信息平台应用
app = FastAPI(
    title="启航引路人 - 留学双边信息平台 API", 
    version="3.0.0", 
    description="连接留学申请者与目标学校学长学姐的专业指导平台",
    lifespan=lifespan
)

# CORS配置（支持前端跨域访问）
# 开发环境和生产环境的动态配置
allowed_origins = [
    "http://localhost:3000",  # Next.js 开发服务器
    "http://127.0.0.1:3000", # 本地回环地址
    "http://localhost:8080",  # 备用前端端口
    "*.vercel.app", # 生产环境域名
    "*.com", # 生产环境 www 域名
]

# 如果是开发环境，允许更多本地端口
if settings.DEBUG:
    allowed_origins.extend([
        "http://localhost:3001",
        "http://localhost:3002", 
        "http://localhost:4173",  # Vite preview
        "http://localhost:5173",  # Vite dev server
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
        "Cache-Control",
    ],
    expose_headers=["Content-Length", "X-Request-ID"],
    max_age=3600,  # 预检请求缓存时间
)

# 信任主机中间件（安全配置）
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "yourdomain.com", "*"]
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    留学平台全局异常处理器
    保护用户隐私，记录错误日志，返回友好错误信息
    """
    # 在生产环境中应使用专业的日志系统
    print(f"🚨 平台错误: {type(exc).__name__}: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "服务器内部错误，请稍后重试",
            "error_id": f"{hash(str(exc)) % 10000000000:010d}"  # 生成错误ID便于追踪
        },
    )

# 注册所有路由模块
from app.api.routers import (
    auth_router, user_router, matching_router, session_router, review_router, message_router, messages
)
# 使用修复后的路由
from app.api.routers.mentor_router_fixed import router as mentor_router_fixed
from app.api.routers.student_router_fixed import router as student_router_fixed
from app.api.routers.service_router_fixed import router as service_router_fixed
# 论坛系统路由
from app.api.routers.forum_router import router as forum_router
# 文件上传路由
from app.api.routers.file_router import router as file_router
# AI智能体系统路由
from app.api.routers.v2_agents_router import router as v2_agents_router
# 保留旧版路由器以确保兼容性
from app.api.routers.planner_router import router as planner_router
# from app.api.routers.advanced_planner_router import router as advanced_planner_router  # 暂时禁用，等待v2架构更新

# 用户认证和管理
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["认证系统"])
app.include_router(user_router.router, prefix="/api/v1/users", tags=["用户管理"])

# 留学平台核心功能
app.include_router(mentor_router_fixed, prefix="/api/v1/mentors", tags=["学长学姐"])
app.include_router(student_router_fixed, prefix="/api/v1/students", tags=["学弟学妹"])
app.include_router(matching_router.router, prefix="/api/v1/matching", tags=["智能匹配"])

# 服务和交易
app.include_router(service_router_fixed, prefix="/api/v1/services", tags=["指导服务"])
app.include_router(session_router.router, prefix="/api/v1/sessions", tags=["指导会话"])

# 评价和反馈
app.include_router(review_router.router, prefix="/api/v1/reviews", tags=["评价反馈"])

# 消息系统 (私信)
app.include_router(messages.router, prefix="/api/messages", tags=["私信"])

# 论坛系统
app.include_router(forum_router, prefix="/api/v1/forum", tags=["论坛系统"])

# 文件上传系统
app.include_router(file_router, prefix="/api/v1/files", tags=["文件上传"])

# AI智能体系统 v2.0 (专注留学规划和咨询)
app.include_router(v2_agents_router, prefix="/api/v2/agents", tags=["AI智能体 v2.0"])

# AI留学规划师 (兼容旧版API)
app.include_router(planner_router, prefix="/api/v1", tags=["AI留学规划师 (兼容)"])
# app.include_router(advanced_planner_router, prefix="/api/v1", tags=["高级AI留学规划师 (兼容)"])  # 暂时禁用，等待v2架构更新

# 静态文件服务 (用于提供上传的文件)
app.mount("/static", StaticFiles(directory="uploads"), name="static")

@app.get("/", summary="平台首页", description="留学双边信息平台API首页")
async def read_root():
    return {
        "message": "欢迎使用启航引路人 - 留学双边信息平台",
        "description": "连接留学申请者与目标学校学长学姐的专业指导平台",
        "version": "3.0.0",
        "features": [
            "🎓 学长学姐指导服务",
            "🎯 智能匹配算法", 
            "📚 专业留学指导",
            "💬 实时沟通交流",
            "⭐ 评价反馈体系",
            "🤖 AI智能体系统 v2.0 (留学规划与咨询)"
        ],
        "ai_agents": {
            "version": "2.0.0",
            "types": ["study_planner", "study_consultant"],
            "api_v2": "/api/v2/agents",
            "status": "/api/v2/agents/status"
        },
        "api_docs": "/docs",
        "health_check": "/health"
    }

@app.get("/health", summary="健康检查", description="检查平台服务状态")
async def health_check():
    return {
        "status": "healthy",
        "service": "留学双边信息平台",
        "version": "3.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }


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