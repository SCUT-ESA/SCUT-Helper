"""
初始化数据库表结构
运行方式：python init_db.py
"""
import asyncio
from config.db_config import async_engine
from models.base import Base
from models.users import User  # 导入所有模型，确保表被创建

async def init_db():
    """创建所有表"""
    async with async_engine.begin() as conn:
        # 删除所有表（可选，开发环境使用）
        # await conn.run_sync(Base.metadata.drop_all)
        
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据库表创建成功！")

if __name__ == "__main__":
    asyncio.run(init_db())
