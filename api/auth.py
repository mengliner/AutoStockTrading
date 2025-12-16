'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-15 16:37:15
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-16 10:44:50
FilePath: \AutoStockTrading\api\auth.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
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
from utils.log_utils import logger  # 日志工具（若无则注释）
import os
from dotenv import load_dotenv

load_dotenv()  # 加载.env文件
SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # 从环境变量获取
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
    # 新增日志：记录接收到的Token（脱敏处理）
    logger.info(f"接收到的Token（前10位）：{token[:10]}...")  # 只打印前10位，避免泄露
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 新增日志：开始解码Token
        logger.info("开始解码Token")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        # 新增日志：记录解码得到的user_id
        logger.info(f"解码得到的user_id: {user_id}，类型: {type(user_id)}")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        # 打印完整错误信息（如过期、签名无效等）
        logger.error(f"Token解码失败：{str(e)}")  # 替换原日志，输出具体错误
        raise credentials_exception
    
    with MySQLClient() as db:
        user = db.query_one("SELECT id, username, role FROM user WHERE id = %s", (user_id,))
        if user is None:
            logger.info(f"根据user_id查询到用户：{user['username']}")
            raise credentials_exception
        return user