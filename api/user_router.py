from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from db.mysql_client import MySQLClient
from api.auth import create_access_token, verify_password, get_password_hash, get_current_user
from utils.log_utils import logger  # 日志工具（若无则注释）
# 新增UUID依赖
import uuid
router = APIRouter(prefix="/api/user")

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(user: UserRegister):
    with MySQLClient() as db:
        if db.get_user_by_username(user.username):
            raise HTTPException(status_code=400, detail="用户名已存在")
        password_hash = get_password_hash(user.password)
        # 生成32位UUID字符串作为用户ID（去除横线后长度为32）
        user_id = str(uuid.uuid4()).replace("-", "")  # 例如："a1b2c3d4e5f6..."
        # 新增用户时插入字符串ID
        if db.create_user(user_id, user.username, password_hash):  # 注意参数新增user_id
            return {"message": "注册成功"}
        raise HTTPException(status_code=500, detail="注册失败")
    
@router.post("/login")
def login(user: UserLogin):
    with MySQLClient() as db:
        db_user = db.get_user_by_username(user.username)
        if not db_user or not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=400, detail="用户名或密码错误")
        # db_user["id"] 已为字符串，直接使用
        token = create_access_token({"sub": db_user["id"]})  # 保持不变
        return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def get_current_user_info(user=Depends(get_current_user)):
    logger.info(f"用户{user['username']}通过Token认证，访问/me接口")
    return user  # 返回当前登录用户信息（id、username、role）