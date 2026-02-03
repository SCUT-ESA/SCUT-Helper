# router/users.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from crud.users import create_user, get_user_by_account, verify_password
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.db_config import get_db
from pydantic import Field
# -------------------------- 定义接口请求/响应模型 --------------------------
router = APIRouter(prefix="/api/users", tags=["用户管理"])  # 接口前缀/api/users，标签分类

# 注册请求体
class RegisterRequest(BaseModel):
    username: str=Field(...,description="用户名",min_length=1,max_length=50)
    account_name: str=Field(...,description="账户名",min_length=1,max_length=20)
    password: str=Field(...,description="密码",min_length=1,max_length=255)

# 登录请求体
class LoginRequest(BaseModel):
    account_name: str=Field(...,description="账户名",min_length=1,max_length=20)
    password: str=Field(...,description="密码",min_length=1,max_length=255)

# -------------------------- 注册接口 --------------------------
@router.post("/register")
async def register(user_info: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册接口"""
    # 1. 先检查账户是否已存在
    existing_user = await get_user_by_account(db, user_info.account_name)
    if existing_user:
        raise HTTPException(status_code=400, detail="账户名已存在")
    
    # 2. 创建用户
    new_user = await create_user(
        db=db,
        username=user_info.username,
        account_name=user_info.account_name,  # 账户名唯一
        password=user_info.password
    )
    
    if not new_user:
        raise HTTPException(status_code=500, detail="注册失败")
    

    # 3. 返回用户信息（隐藏密码哈希）
    return {
        "success": True,
        "message": "注册成功",
        "data": {
            "user_id": new_user.user_id,
            "username": new_user.username,
            "account_name": new_user.account_name
        }
    }

# -------------------------- 登录接口 --------------------------
@router.post("/login")
async def login(login_info: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录接口"""
    # 1. 根据账户名查询用户
    user = await get_user_by_account(db, login_info.account_name)
    if not user:
        # 不暴露“账户不存在”，统一提示“账户名或密码错误”，提升安全性
        raise HTTPException(status_code=401, detail="账户名或密码错误")
    
    # 2. 验证密码
    if not verify_password(login_info.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账户名或密码错误")
    
    # 3. 登录成功（后续可扩展生成token）
    return {
        "success": True,
        "message": "登录成功",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "account_name": user.account_name
        }
    }