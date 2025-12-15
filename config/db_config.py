import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DB"),
    "charset": os.getenv("MYSQL_CHARSET")
}

# Tushare配置
TUSHARE_CONFIG = {
    "token": os.getenv("TUSHARE_TOKEN")
}