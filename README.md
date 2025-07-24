# PeerPotal Backend

一个基于 FastAPI 的社交平台后端项目，支持用户认证、实时聊天和数据检索功能。

## 🚀 快速开始

### 1. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
复制 `env_example.txt` 并创建 `.env` 文件：
```bash
cp env_example.txt .env
```

编辑 `.env` 文件，填入您的 Supabase 配置：
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### 4. 启动服务器
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 功能特性

- ✅ **用户认证**: 注册、登录、JWT Token 验证
- ✅ **数据检索**: 学校和专业信息搜索
- ✅ **实时聊天**: WebSocket 支持
- ✅ **数据库集成**: Supabase PostgreSQL
- ✅ **API 文档**: 自动生成的 Swagger 文档

## 🧪 测试

### 运行所有测试
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行完整测试套件
python test/run_all_tests.py
```

### 单独运行测试
```bash
# API 接口测试
python test/test_api.py

# 数据库测试
python test/test_table_creation.py

# WebSocket 测试
python test/test_ws.py

# Supabase 连接测试
python test/test_supabase.py
```

### 数据库初始化
```bash
python test/setup_database.py
```

## 📚 API 文档

服务器启动后，访问以下链接：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠 项目结构

```
backend/
├── main.py                 # FastAPI 主应用
├── supabase_client.py      # Supabase 客户端配置
├── db_schema.sql          # 数据库表结构
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量配置
├── env_example.txt        # 环境变量示例
└── test/                  # 测试文件夹
    ├── __init__.py
    ├── run_all_tests.py   # 主测试运行器
    ├── test_api.py        # API 接口测试
    ├── test_table_creation.py # 数据库操作测试
    ├── test_ws.py         # WebSocket 测试
    ├── test_supabase.py   # Supabase 连接测试
    └── setup_database.py  # 数据库初始化脚本
```

## 🔧 主要依赖

- **FastAPI**: Web 框架
- **Uvicorn**: ASGI 服务器
- **Supabase**: 数据库和认证
- **python-jose**: JWT 处理
- **passlib**: 密码加密
- **requests**: HTTP 客户端（测试用）

## 📖 使用说明

1. **用户注册**:
   ```bash
   curl -X POST "http://localhost:8000/api/register" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "password": "testpass"}'
   ```

2. **用户登录**:
   ```bash
   curl -X POST "http://localhost:8000/api/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=testuser&password=testpass"
   ```

3. **搜索学校**:
   ```bash
   curl -X GET "http://localhost:8000/api/search?school=哈佛"
   ```

4. **WebSocket 聊天**:
   连接到 `ws://localhost:8000/ws/chat` 进行实时聊天

## 🤝 开发指南

### 添加新的 API 端点
1. 在 `main.py` 中添加新的路由
2. 在 `test/test_api.py` 中添加相应测试
3. 运行测试确保功能正常

### 数据库操作
1. 在 `db_schema.sql` 中定义表结构
2. 在 `test/setup_database.py` 中添加表创建逻辑
3. 在 `test/test_table_creation.py` 中添加测试

## 📝 注意事项

- 确保 Supabase 项目已创建并配置正确
- 测试前请先启动 FastAPI 服务器
- WebSocket 测试需要服务器运行在 localhost:8000
- 数据库测试可能需要适当的 RLS (Row Level Security) 策略
