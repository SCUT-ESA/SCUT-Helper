"""
直接执行SQL创建表（更简单可靠）
运行方式：python init_db_simple.py
"""
import asyncio
from config.db_config import async_engine

# 创建表的SQL语句
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id      CHAR(36)     NOT NULL PRIMARY KEY,
    username     VARCHAR(50)  NOT NULL,
    account_name VARCHAR(20)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

async def init_db():
    """执行SQL创建表"""
    try:
        from sqlalchemy import text
        async with async_engine.begin() as conn:
            await conn.execute(text(CREATE_TABLE_SQL))
            print("✅ 数据库表创建成功！")
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())
