# Peer Portal 后端

## 依赖安装

```bash
pip install -r requirements.txt
```

## 启动 FastAPI 服务

```bash
uvicorn main:app --reload
```

## 环境变量

- `SUPABASE_URL`：Supabase 项目 URL
- `SUPABASE_KEY`：Supabase 服务密钥

## 数据库初始化

将 `db_schema.sql` 在 Supabase SQL Editor 中执行。

## 测试

- 测试 Supabase 连接：
  ```bash
  python test_supabase.py
  ```
- 测试 WebSocket 聊天：
  ```bash
  python test_ws.py
  ```
