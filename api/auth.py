'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-15 16:37:15
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-16 09:19:42
FilePath: \AutoStockTrading\api\auth.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# 配置（可迁移到config目录）
SECRET_KEY = "your-secret-key"  # 生产环境需更换为环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_password_hash(password: str) -> str:
    """生成密码哈希（极简版，避免参数错误）"""
    # 直接传入字符串，passlib会自动转bytes并处理bcrypt限制
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

# 依赖：获取当前登录用户
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from db.mysql_client import MySQLClient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    with MySQLClient() as db:
        user = db.query_one("SELECT id, username, role FROM user WHERE id = %s", (user_id,))
        if user is None:
            raise credentials_exception
        return user