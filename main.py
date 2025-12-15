'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-13 14:45:33
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-15 16:43:32
FilePath: \AutoStockTrading\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from db.mysql_client import MySQLClient
from data.tushare_client import TushareClient
from data.csv_client import CSVClient  # 新增导入
from utils.log_utils import logger  # 日志工具（若无则注释）
import time
from fastapi import FastAPI
from api.stock_router import router as stock_router
from api.user_router import router as user_router

app = FastAPI()
app.include_router(stock_router)
app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn
    # 启动API服务（如需执行数据导入，可先调用main()）
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)