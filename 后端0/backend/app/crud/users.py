# crud/users.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import bcrypt
from sqlalchemy import select
from models.users import User  # 导入ORM模型

# -------------------------- 注册相关 --------------------------
async def create_user(db: AsyncSession, username: str, account_name: str, password: str):
    """
    创建新用户（注册）
    :param db: 数据库会话
    :param username: 用户名
    :param account_name: 账户名（唯一）
    :param password: 原始密码（前端传入，后端哈希后存储）
    :return: 新建的用户对象 / 错误信息
    """
    # 1. 密码哈希（BCrypt，自带盐值，不可逆）
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()  # 生成随机盐值
    password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
    
    # 2. 创建User对象
    db_user = User(
        username=username,
        account_name=account_name,  # 账户名唯一
        password_hash=password_hash
    )

    try:
        # 3. 写入数据库
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)  # 刷新对象，获取完整字段（如自动生成的user_id）
        print("-"*20)
        print(db_user)
        return db_user
    except IntegrityError:
        # 捕获账户名重复的异常
        await db.rollback()
        return None

# -------------------------- 登录相关 --------------------------
async def get_user_by_account(db: AsyncSession, account_name: str):
    """根据账户名查询用户"""
    result =await db.execute(select(User).where(User.account_name == account_name))
    return result.scalars().first()

def verify_password(plain_password: str, hashed_password: str):
    """验证原始密码和哈希密码是否匹配"""
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)
