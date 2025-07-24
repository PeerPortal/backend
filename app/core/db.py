"""
数据库连接池管理模块
使用 asyncpg 创建高性能的异步 PostgreSQL 连接池
"""
import asyncpg
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator
import logging

from app.core.config import settings

# 全局数据库连接池
db_pool: asyncpg.Pool = None
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器
    初始化和清理应用资源
    """
    global db_pool
    logger.info("初始化数据库连接池...")
    
    try:
        # 尝试获取数据库连接字符串
        postgres_url = settings.postgres_url
        
        # 创建连接池
        db_pool = await asyncpg.create_pool(
            dsn=postgres_url,
            min_size=settings.DB_POOL_MIN_SIZE,
            max_size=settings.DB_POOL_MAX_SIZE,
            command_timeout=60,
            server_settings={'jit': 'off'}
        )
        logger.info("数据库连接池创建成功")
        
    except ValueError as e:
        # 配置错误（如缺少密码）
        logger.warning(f"数据库配置不完整: {e}")
        logger.info("应用将在降级模式下运行（仅支持 Supabase REST API）")
        db_pool = None
        
    except Exception as e:
        # 其他连接错误
        logger.error(f"无法创建数据库连接池: {e}")
        logger.info("应用将在降级模式下运行（仅支持 Supabase REST API）")
        db_pool = None

    # 应用运行期间
    yield
    
    # 清理资源
    if db_pool:
        logger.info("关闭数据库连接池...")
        await db_pool.close()
        logger.info("数据库连接池已关闭")


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    获取数据库连接的依赖注入函数
    """
    if not db_pool:
        raise RuntimeError(
            "数据库连接池未初始化。请检查数据库配置或使用 Supabase REST API。"
        )
    
    async with db_pool.acquire() as connection:
        yield connection


async def check_db_health() -> bool:
    """
    检查数据库连接健康状态
    """
    if not db_pool:
        logger.warning("数据库连接池未初始化")
        return False
        
    try:
        async with db_pool.acquire() as connection:
            await connection.fetchval("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return False


# 直接执行查询的辅助函数（用于测试）
async def execute_query(query: str, *args):
    """
    直接执行查询（需要连接池）
    """
    if not db_pool:
        raise RuntimeError("数据库连接池未初始化")
        
    async with db_pool.acquire() as connection:
        return await connection.fetch(query, *args)


async def execute_command(command: str, *args):
    """
    执行命令（INSERT/UPDATE/DELETE）
    """
    if not db_pool:
        raise RuntimeError("数据库连接池未初始化")
        
    async with db_pool.acquire() as connection:
        return await connection.execute(command, *args) 