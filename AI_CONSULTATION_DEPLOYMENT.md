# 🚀 留学申请AI咨询系统部署指南

## 📋 系统概览

本系统是一个基于LLM的智能留学申请咨询平台，包含背景分析、学校推荐、申请策略制定和实时智能对话功能。

## 🏗️ 系统架构

```
┌─────────────────────────────────────┐
│             前端层                   │
│  React + WebSocket + 实时聊天界面     │
├─────────────────────────────────────┤
│             API网关层                │
│     FastAPI + JWT认证 + 路由管理      │
├─────────────────────────────────────┤
│            AI服务层                  │
│  OpenAI API + 提示工程 + 结果解析     │
├─────────────────────────────────────┤
│           业务逻辑层                 │
│ 背景分析 + 学校推荐 + 策略生成 + 聊天  │
├─────────────────────────────────────┤
│            数据层                    │
│ PostgreSQL + Redis + 向量数据库       │
└─────────────────────────────────────┘
```

## 🛠️ 技术栈

### 后端技术栈
- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 15+ (主数据库)
- **缓存**: Redis 7+ (会话缓存)
- **向量数据库**: pgvector (知识库检索)
- **AI服务**: OpenAI GPT-4, Anthropic Claude-3
- **认证**: JWT + bcrypt
- **部署**: Docker + Kubernetes

### 前端技术栈
- **框架**: React 18+ + TypeScript
- **状态管理**: Zustand / Redux Toolkit
- **UI组件**: Tailwind CSS + HeadlessUI
- **实时通信**: WebSocket / Socket.IO
- **构建工具**: Vite / Next.js

## 📦 安装部署

### 1. 环境准备

#### 系统要求
- Python 3.9+
- Node.js 16+
- PostgreSQL 15+
- Redis 7+
- Docker (可选)

#### 依赖安装
```bash
# 克隆项目
git clone <repository-url>
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装Python依赖
pip install -r requirements.txt

# 安装额外的AI咨询依赖
pip install openai anthropic tiktoken numpy pandas scikit-learn
```

### 2. 数据库配置

#### PostgreSQL设置
```sql
-- 创建数据库
CREATE DATABASE study_abroad_ai;

-- 安装pgvector扩展 (用于向量搜索)
CREATE EXTENSION vector;

-- 导入AI咨询系统表结构
\i ai_consultation_schema.sql
```

#### 环境变量配置
创建 `.env` 文件：
```env
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/study_abroad_ai
REDIS_URL=redis://localhost:6379/0

# AI服务配置
OPENAI_API_KEY=sk-your-openai-api-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
AI_MODEL_PRIMARY=gpt-4  # 主要使用的模型
AI_MODEL_FALLBACK=gpt-3.5-turbo  # 备用模型

# Supabase配置 (如果使用)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# 应用配置
APP_NAME=留学申请AI咨询系统
SECRET_KEY=your-super-secret-key
DEBUG=true
HOST=0.0.0.0
PORT=8001

# 安全配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 文件存储
UPLOAD_MAX_SIZE=10485760  # 10MB
UPLOAD_ALLOWED_EXTENSIONS=pdf,doc,docx,txt

# 限流配置
RATE_LIMIT_PER_MINUTE=60
AI_REQUESTS_PER_DAY=100
```

### 3. API集成配置

#### 创建AI服务配置文件
```python
# app/core/ai_config.py
from typing import Dict, List
import os

class AIConfig:
    """AI服务配置"""
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL_PRIMARY = os.getenv("AI_MODEL_PRIMARY", "gpt-4")
    OPENAI_MODEL_FALLBACK = os.getenv("AI_MODEL_FALLBACK", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS = 2000
    OPENAI_TEMPERATURE = 0.7
    
    # Anthropic配置
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = "claude-3-sonnet-20240229"
    
    # 成本控制
    MAX_TOKENS_PER_USER_PER_DAY = 50000
    MAX_REQUESTS_PER_USER_PER_HOUR = 20
    
    # 提示词配置
    SYSTEM_PROMPTS = {
        "analysis": """你是一位资深的留学申请顾问，拥有15年的申请指导经验...""",
        "recommendation": """你是一位经验丰富的留学顾问，熟悉全球各大学的录取要求...""",
        "strategy": """你是一位留学申请策略专家，擅长制定详细的申请计划...""",
        "chat": """你是一位亲切、专业的留学申请顾问AI助手，名字叫"小申"..."""
    }
```

### 4. 启动服务

#### 开发环境启动
```bash
# 启动Redis (如果没有服务)
redis-server

# 启动PostgreSQL (如果没有服务)
pg_ctl start

# 启动FastAPI应用
python start_new_app.py

# 或使用uvicorn直接启动
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 验证启动
```bash
# 检查API健康状态
curl http://localhost:8001/health

# 检查API文档
curl http://localhost:8001/docs
```

### 5. 前端部署

#### React应用构建
```bash
cd frontend

# 安装依赖
npm install

# 安装额外依赖
npm install @heroicons/react lucide-react axios socket.io-client

# 创建环境配置
echo "VITE_API_BASE_URL=http://localhost:8001" > .env.local

# 开发模式启动
npm run dev

# 生产构建
npm run build
```

## 🔧 配置优化

### 1. 数据库优化

#### PostgreSQL性能优化
```sql
-- 增加连接池大小
ALTER SYSTEM SET max_connections = 200;

-- 优化内存设置
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '4MB';

-- 创建必要索引
CREATE INDEX CONCURRENTLY idx_chat_messages_session_timestamp 
ON chat_messages(session_id, created_at);

CREATE INDEX CONCURRENTLY idx_consultation_sessions_user_activity 
ON consultation_sessions(user_id, last_activity);

-- 设置自动清理
ALTER TABLE chat_messages SET (autovacuum_vacuum_scale_factor = 0.1);
```

#### Redis配置优化
```redis
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 2. AI服务优化

#### 成本控制策略
```python
# app/services/ai_cost_control.py
class AICostController:
    """AI成本控制器"""
    
    def __init__(self):
        self.daily_limits = {
            "free_user": 10,      # 免费用户每日10次
            "premium_user": 100,   # 付费用户每日100次
            "enterprise": 1000     # 企业用户每日1000次
        }
    
    async def check_usage_limit(self, user_id: int, user_tier: str) -> bool:
        """检查用户使用限制"""
        today_usage = await self.get_today_usage(user_id)
        limit = self.daily_limits.get(user_tier, 10)
        return today_usage < limit
    
    async def log_ai_usage(self, user_id: int, model: str, 
                          tokens_used: int, cost: float):
        """记录AI使用情况"""
        # 实现使用记录逻辑
        pass
```

#### 智能模型选择
```python
# app/services/model_selector.py
class ModelSelector:
    """智能模型选择器"""
    
    def select_model(self, task_type: str, user_tier: str, 
                    complexity: str = "medium") -> str:
        """根据任务类型和用户等级选择最适合的模型"""
        
        if user_tier == "enterprise" or complexity == "high":
            return "gpt-4"
        elif task_type in ["analysis", "recommendation"]:
            return "gpt-4"  # 核心功能使用高质量模型
        else:
            return "gpt-3.5-turbo"  # 日常对话使用经济模型
```

### 3. 缓存策略

#### Redis缓存配置
```python
# app/core/cache.py
import redis
import json
from typing import Any, Optional

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis_client = redis.from_url(os.getenv("REDIS_URL"))
        self.default_ttl = 3600  # 1小时
    
    async def cache_analysis_result(self, profile_hash: str, 
                                  analysis: dict, ttl: int = 86400):
        """缓存分析结果 (24小时)"""
        key = f"analysis:{profile_hash}"
        await self.redis_client.setex(
            key, ttl, json.dumps(analysis)
        )
    
    async def cache_school_recommendations(self, profile_hash: str, 
                                         recommendations: list, ttl: int = 43200):
        """缓存学校推荐 (12小时)"""
        key = f"recommendations:{profile_hash}"
        await self.redis_client.setex(
            key, ttl, json.dumps(recommendations)
        )
```

## 🐳 Docker部署

### 1. Dockerfile配置

#### 后端Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### 前端Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# 复制依赖文件
COPY package*.json ./
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 使用nginx提供静态文件
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2. Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: study_abroad_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./ai_consultation_schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  backend:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/study_abroad_ai
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    ports:
      - "8001:8001"
    volumes:
      - ./uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

### 3. 部署命令

```bash
# 构建并启动所有服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

## 🔐 安全配置

### 1. API安全

#### 限流配置
```python
# app/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# 应用级限流
@limiter.limit("100/minute")
async def api_endpoint():
    pass

# AI请求特殊限流
@limiter.limit("10/minute")
async def ai_consultation_endpoint():
    pass
```

#### 输入验证
```python
# app/middleware/input_validation.py
from pydantic import validator
import bleach

class SecureInput(BaseModel):
    content: str
    
    @validator('content')
    def sanitize_content(cls, v):
        # 清理HTML标签
        cleaned = bleach.clean(v, tags=[], strip=True)
        # 限制长度
        if len(cleaned) > 5000:
            raise ValueError('输入内容过长')
        return cleaned
```

### 2. 数据安全

#### 敏感信息加密
```python
# app/core/encryption.py
from cryptography.fernet import Fernet
import os

class DataEncryption:
    """数据加密工具"""
    
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY").encode()
        self.cipher = Fernet(self.key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感数据"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

## 📊 监控配置

### 1. 应用监控

#### Prometheus监控
```python
# app/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest

# 定义指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
AI_REQUESTS = Counter('ai_requests_total', 'Total AI requests', ['model', 'operation'])

@app.middleware("http")
async def add_prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    REQUEST_COUNT.inc()
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response
```

#### 健康检查端点
```python
# app/api/health.py
@router.get("/health")
async def health_check():
    """健康检查端点"""
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "ai_service": await check_ai_service(),
        "disk_space": check_disk_space()
    }
    
    is_healthy = all(checks.values())
    status_code = 200 if is_healthy else 503
    
    return JSONResponse(
        content={"status": "healthy" if is_healthy else "unhealthy", "checks": checks},
        status_code=status_code
    )
```

### 2. 日志配置

#### 结构化日志
```python
# app/core/logging.py
import structlog
import logging

def setup_logging():
    """配置结构化日志"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

## 🚀 生产部署

### 1. Kubernetes部署

#### 部署配置
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-consultation-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-consultation-backend
  template:
    metadata:
      labels:
        app: ai-consultation-backend
    spec:
      containers:
      - name: backend
        image: your-registry/ai-consultation:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-secret
              key: openai-key
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
```

### 2. CI/CD流水线

#### GitHub Actions配置
```yaml
# .github/workflows/deploy.yml
name: Deploy AI Consultation System

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest
    - name: Run tests
      run: pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      run: |
        # 部署脚本
        echo "Deploying to production..."
```

## 📈 扩展性考虑

### 1. 微服务架构

```
AI咨询系统 → 拆分为：
├── 用户认证服务 (auth-service)
├── 背景分析服务 (analysis-service)  
├── 学校推荐服务 (recommendation-service)
├── 聊天服务 (chat-service)
├── 通知服务 (notification-service)
└── 文件服务 (file-service)
```

### 2. 负载均衡

```nginx
# nginx.conf
upstream backend {
    server backend-1:8001;
    server backend-2:8001;
    server backend-3:8001;
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

这个部署指南为你的AI咨询系统提供了完整的生产环境部署方案。你可以根据实际需求选择合适的部署方式，从简单的单机部署到复杂的Kubernetes集群都有涵盖。
