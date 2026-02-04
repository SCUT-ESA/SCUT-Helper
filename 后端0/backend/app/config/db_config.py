from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column
from sqlalchemy import DateTime,String,func,Float
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

# 获取app目录路径（db_config.py在app/config/目录下，所以需要向上两级）
BASE_DIR = Path(__file__).resolve().parent.parent
# 加载 .env 文件（在app目录下）
env_path = BASE_DIR / '.env'
print(f"正在加载 .env 文件: {env_path}")
print(f".env 文件是否存在: {env_path.exists()}")
load_dotenv(env_path)

# 调试：打印读取到的环境变量
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

print(f"DB_USER: {DB_USER}")
print(f"DB_PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'None'}")
print(f"DB_HOST: {DB_HOST}")
print(f"DB_PORT: {DB_PORT}")
print(f"DB_NAME: {DB_NAME}")

# 对密码进行URL编码（处理特殊字符如@等）
encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""

# 数据库URL
ASYNC_DATABASE_URL = (
    f"mysql+aiomysql://"
    f"{DB_USER}:{encoded_password}"
    f"@{DB_HOST}:{DB_PORT}"
    f"/{DB_NAME}"
    f"?charset={os.getenv('DB_CHARSET', 'utf8mb4')}"
)
print(f"数据库连接URL: mysql+aiomysql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
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