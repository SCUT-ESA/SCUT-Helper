from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column
from sqlalchemy import DateTime,String,func,Float
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()
# 数据库URL
ASYNC_DATABASE_URL = (
    f"mysql+aiomysql://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
    f"/{os.getenv('DB_NAME')}"
    f"?charset={os.getenv('DB_CHARSET', 'utf8mb4')}"
)
#创建数据库引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=True,
    pool_size=10,
    max_overflow=20,
                                   )

#创建数据库会话
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,#绑定数据库引擎
    class_=AsyncSession,#指定会话类
    expire_on_commit=False,#提交会话后不过期，不会重新查询数据库
    )

#依赖项
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session #返回数据库会话给路由处理函数
            await session.commit() #提交事务
        except Exception:
            await session.rollback()#有异常，回滚
            raise
        finally:
            await session.close()#关闭会话