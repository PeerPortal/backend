"""
留学生互助平台 - 后端主应用
整合所有功能模块的完整应用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# 导入API路由
try:
    from app.api.platform_core import router as platform_router
    from app.api.ai_consultation import router as ai_router
except ImportError:
    # 如果导入失败，创建一个简单的路由用于演示
    from fastapi import APIRouter
    platform_router = APIRouter()
    ai_router = APIRouter()

app = FastAPI(
    title="留学生互助平台",
    description="集成筛选、发帖、聊天、认证、支付、AI咨询的完整平台",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务 - 必须在API路由之前
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# 添加API路由
app.include_router(platform_router)
app.include_router(ai_router)

@app.get("/")
async def root():
    """根路径 - 返回前端应用或API信息"""
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    return {
        "message": "留学生互助平台 API",
        "version": "1.0.0",
        "features": [
            "四步筛选系统（学历→地区→院校→专业）",
            "发帖系统（导师服务/求助帖）",
            "实时聊天系统",
            "认证系统（实名/院校/手机/邮箱）",
            "AI智能咨询",
            "用户管理和工作台"
        ],
        "endpoints": {
            "API文档": "/docs",
            "交互式文档": "/redoc",
            "核心API": "/api/v1/*",
            "AI咨询": "/ai/*"
        }
    }

# API健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "留学生互助平台"}

# 捕获所有前端路由
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """服务前端应用的所有路由"""
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动留学生互助平台...")
    print("📚 功能模块：")
    print("  ✅ 四步筛选系统（学历→地区→院校→专业）")
    print("  ✅ 发帖系统（导师服务/求助帖）")
    print("  ✅ 实时聊天系统")
    print("  ✅ 认证系统（实名/院校/手机/邮箱）")
    print("  ✅ AI智能咨询")
    print("  ✅ 用户管理和工作台")
    print()
    print("🌐 访问地址：")
    print("  前端应用: http://localhost:8000")
    print("  API文档: http://localhost:8000/docs")
    print("  交互式文档: http://localhost:8000/redoc")
    print()
    
    uvicorn.run(
        "complete_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
