## 环境

conda activate offerin

# 启航引路人后端项目开发指南

本文档为后端项目的开发、数据库交互、测试和模块化开发提供了统一的规范和最佳实践。

## 1. 技术栈概览

- **框架**: FastAPI
- **数据库**: PostgreSQL (通过 Supabase 托管)
- **数据库交互**: 
  - **首选**: `asyncpg` 连接池，用于高性能直接数据库访问。
  - **备用**: `supabase-py` 客户端，用于在无直接连接环境下的 RESTful API 访问。
- **测试**: `pytest`
- **代码规范**: `black`, `isort`, `flake8`

## 2. API 开发规范

所有 API 开发应遵循 RESTful 原则。

### 2.1. 目录结构

- **路由**: `app/api/routers/`
- **模型 (Schemas)**: `app/schemas/`
- **业务逻辑 (CRUD)**: `app/crud/`
- **核心配置与连接**: `app/core/`

### 2.2. 路由 (Routers)

- 每个主要功能模块（如论坛、用户、消息）都应有独立的路由文件。例如：`app/api/routers/forum_router.py`。
- 使用 `APIRouter` 进行模块化管理，并在 `app/main.py` 中统一注册。
- 路径操作函数应清晰、简洁，主要负责处理 HTTP 请求和响应，并将复杂的业务逻辑委托给 CRUD 层。

### 2.3. 数据模型 (Schemas)

- 使用 Pydantic 模型定义所有请求体、响应体和数据对象。
- 为每个核心实体（如 `Post`, `User`）创建基础模型、创建模型、更新模型和数据库模型。
- 示例 (`app/schemas/forum_schema.py`):

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 定义作者信息，用于嵌套在帖子和回复中
class ForumAuthor(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None

# 创建帖子时使用的模型
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=50000)
    category: str
    tags: List[str] = []

# 从数据库返回的完整帖子模型
class ForumPost(BaseModel):
    id: int
    title: str
    content: str
    author: ForumAuthor  # 嵌套作者信息
    category: str
    tags: List[str]
    replies_count: int = 0
    likes_count: int = 0
    views_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

## 3. 数据库交互指南

数据库交互是项目的核心，必须遵循双模式策略以确保灵活性和鲁棒性。

### 3.1. 双模式数据库访问

本项目设计了两种数据库访问方式：

1.  **`asyncpg` 连接池**: 生产环境和高性能场景下的首选。通过 `app.core.db.get_db_connection` 获取连接。
2.  **Supabase 客户端**: 作为备用或在无法直接连接数据库的环境中使用。通过 `app.core.supabase_client.get_supabase_client` 获取客户端实例。

**所有 CRUD 函数都必须同时支持这两种模式。**

### 3.2. CRUD 层实现

- 所有数据库操作必须封装在 `app/crud/` 目录下的相应文件中（例如 `app/crud/crud_forum.py`）。
- CRUD 函数的第一个参数应为 `db_conn: Dict[str, Any]`，它包含连接/客户端实例和类型信息。
- 在函数内部，通过检查 `db_conn['type']` 来决定使用 `asyncpg` 还是 `supabase-py`。

- **关键实现模式** (参考 `crud_forum.py`):

```python
from typing import Dict, Any, Optional
from app.schemas.forum_schema import ForumPost

# 这是一个辅助函数，用于将数据库记录映射到 Pydantic Schema
async def _map_post_record_to_schema(record: Dict[str, Any]) -> ForumPost:
    # ... (此处省略了具体的映射逻辑, 详见 crud_forum.py)
    pass

class ForumCRUD:
    async def get_post_by_id(self, db_conn: Dict[str, Any], post_id: int, user_id: Optional[int] = None) -> Optional[ForumPost]:
        """通过ID获取单个帖子，如果找不到则返回None"""
        try:
            # 优先使用 Supabase 客户端
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                
                # 查询帖子，并带上作者信息、点赞数和回复数
                query = client.table("forum_posts").select(
                    "*, author:users(*), likes_count:forum_likes(count), replies_count:forum_replies(count)"
                ).eq('id', post_id)
                
                result = query.execute()

                if not result.data:
                    return None
                
                record = result.data[0]

                # 如果提供了 user_id，则检查当前用户是否点赞了该帖子
                if user_id:
                    liked_res = client.table('forum_likes').select('post_id').eq('user_id', user_id).eq('post_id', post_id).execute()
                    record['is_liked'] = len(liked_res.data) > 0
                else:
                    record['is_liked'] = False

                # 将字典格式的记录映射为 Pydantic 模型实例
                return await _map_post_record_to_schema(record)
            else:
                # asyncpg 的逻辑（在当前版本中未完全实现）
                # conn = db_conn["connection"]
                # ...
                return None
        except Exception as e:
            # 记录异常，避免服务崩溃
            print(f"获取帖子详情时发生异常: {e}")
            return None
```

### 3.3. 依赖注入

在 API 路由中，使用 `app.api.deps.get_db` 作为依赖项来获取数据库连接。此函数会自动处理使用 `asyncpg` 还是 Supabase 客户端的逻辑。

```python
from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.api import deps

router = APIRouter()

@router.get("/{post_id}")
async def read_post(post_id: int, db: Dict[str, Any] = Depends(deps.get_db)):
    # ...
```

## 4. 数据库表结构管理

- **主要管理方式**: 所有数据表的创建、修改和删除操作，都应通过 **Supabase 后台的图形化界面** 完成。
- **禁止**: 禁止直接在生产数据库中手动执行 `ALTER TABLE` 等危险操作，除非有充分理由并经过审查。
- **架构同步**: 在对表结构进行任何更改后，开发者有责任将最新的数据库结构导出为 SQL 文件，并更新到项目中的 `scripts/database/db_schema.sql` 文件。这有助于团队成员了解最新的表结构，并用于搭建本地测试环境。

## 5. 测试规范

为确保代码质量和功能稳定性，所有新的 API 端点和核心业务逻辑都必须编写单元测试和集成测试。

### 5.1. 测试框架

- 使用 `pytest` 作为主要的测试框架。
- 异步代码测试需配合 `pytest-asyncio`。

### 5.2. 测试文件结构

- 所有测试文件都应放置在 `test/` 目录下，并与 `app/` 的结构保持一致。
- API 测试: `test/api/test_forum_api.py`
- CRUD 测试: `test/crud/test_crud_forum.py`

### 5.3. 测试数据库

- 测试应在独立的测试数据库或专门的 Supabase 测试项目中运行，以避免污染开发或生产数据。
- 配置文件 `.env.test` 用于存储测试环境的数据库连接信息。

### 5.4. 测试示例

一个典型的 API 测试用例 (`test/api/test_forum_api.py`):

```python
import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, normal_user_token_headers: dict):
    response = await client.post(
        "/api/v1/forum/posts/",
        headers=normal_user_token_headers,
        json={"title": "测试帖子", "content": "这是一个测试内容", "category": "test"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "测试帖子"
    assert "id" in data
```

## 6. 模块开发指南

### 6.1. 论坛模块

- **核心文件**: `crud_forum.py`, `forum_schema.py`, `forum_router.py`
- **数据库交互**: 严格遵循 3.2 节定义的双模式策略。
- **测试**: 重点测试帖子的增删改查、回复、点赞等功能。

### 6.2. 私信模块

- **核心文件**: `crud_message.py`, `message_schema.py`, `message_router.py`
- **数据库交互**: 同样需要支持双模式。考虑到实时性，未来可能引入 WebSocket，相关逻辑需在 `message_router.py` 中处理。
- **测试**: 测试消息发送、接收、读取状态更新和会话列表获取。

### 6.3. 支付模块 (待开发)

- **核心文件**: `crud_payment.py`, `payment_schema.py`, `payment_router.py`
- **数据库交互**: 支付记录的创建和状态更新至关重要，必须保证事务的原子性和数据一致性。在 `asyncpg` 模式下，应使用数据库事务。
- **安全**: 支付接口必须有严格的权限控制和输入验证，防止未授权访问和注入攻击。
- **测试**: 模拟支付回调，测试订单状态的变更是否正确。