#!/bin/bash

echo "🚀 启动留学生互助平台完整应用"
echo "================================"

# 检查Python和Node.js
echo "📋 检查环境..."
python3 --version || { echo "❌ 需要安装Python 3.7+"; exit 1; }
node --version || { echo "❌ 需要安装Node.js"; exit 1; }

# 安装Python依赖
echo "📦 安装Python依赖..."
pip install fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt] sqlalchemy psycopg2-binary openai || {
    echo "❌ Python依赖安装失败"
    exit 1
}

# 检查前端目录
if [ -d "frontend" ]; then
    echo "📦 安装Node.js依赖..."
    cd frontend
    npm install || {
        echo "❌ Node.js依赖安装失败"
        exit 1
    }
    
    echo "🏗️ 构建前端应用..."
    npm run build || {
        echo "❌ 前端构建失败"
        exit 1
    }
    cd ..
else
    echo "⚠️ 前端目录不存在，将仅启动API服务"
fi

# 启动应用
echo "🚀 启动应用服务器..."
echo ""
echo "🌐 访问地址："
echo "  前端应用: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo "  交互式文档: http://localhost:8000/redoc"
echo ""
echo "📚 功能模块："
echo "  ✅ 四步筛选系统（学历→地区→院校→专业）"
echo "  ✅ 发帖系统（导师服务/求助帖）"
echo "  ✅ 实时聊天系统"
echo "  ✅ 认证系统（实名/院校/手机/邮箱）"
echo "  ✅ AI智能咨询"
echo "  ✅ 用户管理和工作台"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================"

python3 complete_app.py
