# PeerPotal Backend

一个基于 FastAPI 的社交平台后端项目，支持用户认证、实时聊天和数据检索功能。

**🎉 项目已升级为企业级模块化架构！**

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

编辑 `.env` 文件，填入您的配置：
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
DEBUG=true
```

### 4. 初始化数据库
```bash
# 在 Supabase SQL Editor 中执行 db_schema.sql
# 然后运行初始化脚本
python test/setup_database.py
```

### 5. 启动应用
```bash
# 推荐：使用新的企业级架构
python start_new_app.py

# 服务将运行在 http://localhost:8001
```

## 📋 功能特性

- ✅ **企业级架构**: 模块化分层设计
- ✅ **用户认证**: JWT + 角色权限控制
- ✅ **用户资料**: 完整的资料管理系统
- ✅ **数据库**: asyncpg 连接池 + 事务支持
- ✅ **API 文档**: 自动生成的交互式文档
- ✅ **实时聊天**: WebSocket 支持
- ✅ **健康检查**: 监控和诊断端点
- ✅ **错误处理**: 全局异常处理和日志

## 🛠 项目架构

### 新架构（推荐）
```
app/                       # 企业级模块化架构
├── api/                   # API 层
│   ├── deps.py           # 认证依赖注入
│   └── routers/          # 路由模块
│       ├── auth_router.py    # 认证 API
│       └── user_router.py    # 用户 API
├── core/                 # 核心配置
│   ├── config.py         # 环境配置管理
│   └── db.py             # 数据库连接池
├── crud/                 # 数据库操作层
│   └── crud_user.py      # 用户相关操作
├── schemas/              # 数据模型
│   ├── token_schema.py   # JWT 模型
│   └── user_schema.py    # 用户模型
└── main.py               # 主应用入口
```

### 支持文件
```
test/                     # 测试系统
├── test_new_api.py      # 新架构 API 测试
├── setup_database.py   # 数据库初始化
├── check_database.py   # 数据库检查
├── test_ws.py          # WebSocket 测试
└── run_all_tests.py    # 主测试运行器

legacy_backup/           # 旧版本备份
db_schema.sql           # 数据库架构
start_new_app.py        # 应用启动脚本
PROJECT_MIGRATION_SUMMARY.md  # 架构升级总结
```

## 🧪 测试

### 运行完整测试套件
```bash
python test/run_all_tests.py
```

### 单独运行测试
```bash
# 新架构 API 测试
python test/test_new_api.py

# 数据库初始化和检查
python test/setup_database.py
python test/check_database.py

# WebSocket 测试
python test/test_ws.py
```

## 📚 API 文档

启动应用后访问：
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **健康检查**: http://localhost:8001/health

## 🔧 主要依赖

**核心框架:**
- **FastAPI**: 高性能 Web 框架
- **Uvicorn**: ASGI 服务器
- **Pydantic**: 数据验证和序列化

**数据库:**
- **asyncpg**: 高性能异步 PostgreSQL 驱动
- **Supabase**: 数据库和认证服务

**认证和安全:**
- **python-jose**: JWT 处理
- **passlib**: 密码加密
- **email-validator**: 邮箱验证

## 📖 API 使用示例

### 1. 用户注册
```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "securepassword"
     }'
```

### 2. 用户登录
```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=securepassword"
```

### 3. 获取用户资料
```bash
curl -X GET "http://localhost:8001/api/v1/users/me" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. 更新用户资料
```bash
curl -X PUT "http://localhost:8001/api/v1/users/me" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Test User",
       "bio": "This is my bio"
     }'
```

## 🔄 架构升级

项目已从简单原型升级为企业级架构：

| 方面 | 旧版本 | 新架构 |
|------|--------|--------|
| **结构** | 单文件应用 | 模块化分层 |
| **配置** | 硬编码 | Pydantic Settings |
| **数据库** | 简单客户端 | 连接池 + 事务 |
| **认证** | 内存存储 | JWT + 数据库 |
| **错误处理** | 基础 | 全局处理器 |
| **API 文档** | 简单 | 完整交互式 |
| **生产就绪** | ❌ | ✅ |

详细升级信息请查看 [`PROJECT_MIGRATION_SUMMARY.md`](PROJECT_MIGRATION_SUMMARY.md)

## 🤝 开发指南

### 添加新功能
1. 在 `app/schemas/` 中定义数据模型
2. 在 `app/crud/` 中实现数据库操作
3. 在 `app/api/routers/` 中创建 API 路由
4. 在 `app/main.py` 中注册路由
5. 添加相应的测试

### 数据库操作
1. 更新 `db_schema.sql`
2. 在 Supabase 中执行 SQL
3. 运行 `python test/setup_database.py` 验证

### 部署准备
1. 设置 `DEBUG=false`
2. 更新 `SECRET_KEY`
3. 配置生产数据库
4. 设置 CORS 域名

## 📝 注意事项

- 确保 Supabase 项目已正确配置
- 新架构运行在端口 8001（避免端口冲突）
- 旧版本文件已备份到 `legacy_backup/` 目录
- 完整的类型提示和数据验证
- 异步操作和连接池优化

## 🆘 故障排除

**常见问题:**

1. **配置错误**: 检查 `.env` 文件配置
2. **数据库连接**: 运行 `python test/check_database.py`
3. **端口冲突**: 新架构使用端口 8001
4. **依赖问题**: 重新安装 `pip install -r requirements.txt`

**获取帮助:**
- 查看 API 文档: http://localhost:8001/docs
- 检查日志输出
- 运行测试套件诊断问题

---

🎉 **项目现在拥有企业级的后端架构，为未来的功能扩展做好了充分准备！**
