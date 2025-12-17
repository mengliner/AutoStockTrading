'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-15 16:38:45
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-17 09:58:01
FilePath: \AutoStockTrading\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# main.py
# -*- coding: utf-8 -*-
import uvicorn
import signal
import sys
from fastapi import FastAPI
from api.stock_router import router as stock_router
from api.user_router import router as user_router
from api.task_router import router as task_router
from utils.scheduler import scheduler
from utils.task_manager import task_manager
from service.daily_k_service import sync_yesterday_daily_k
from utils.log_utils import logger
from db import create_all_tables
from db.mysql_client import MySQLClient

# ----------------------
# 全局退出信号处理
# ----------------------
def handle_shutdown(signum, frame):
    """处理服务退出信号（Ctrl+C/系统终止）"""
    logger.info("🛑 接收到退出信号，正在停止服务...")
    # 停止调度器
    scheduler.stop()
    logger.info("✅ 调度器已停止")
    # 退出程序
    sys.exit(0)

# 注册退出信号处理（兼容Windows/Linux）
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

# ----------------------
# 初始化：任务注册 + 调度器启动
# ----------------------
def init_tasks():
    """初始化定时任务（项目启动时执行一次）"""
    # 1. 确保数据表已创建
    with MySQLClient() as db:
        create_all_tables(db)
    
    # 2. 从数据库加载任务并启动调度器
    scheduler.load_jobs_from_db()
    scheduler.start()
    logger.info("✅ 基于数据库的定时任务调度器已启动")

# ----------------------
# FastAPI应用初始化
# ----------------------
app = FastAPI(title="股票数据分析系统", version="1.0")

# 注册路由
app.include_router(stock_router)
app.include_router(user_router)
app.include_router(task_router)

# ----------------------
# 启动入口
# ----------------------
if __name__ == "__main__":
    try:
        # 初始化任务
        init_tasks()
        logger.info("🚀 股票数据分析系统启动中...")
        # 启动FastAPI服务（禁用reload，避免多进程问题）
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # 关键：禁用热重载，避免多进程导致的线程管理问题
            log_level="info",
            workers=1  # 单进程运行，保证定时任务唯一
        )
    except Exception as e:
        logger.error(f"❌ 服务启动失败：{str(e)}", exc_info=True)
        # 异常时停止调度器
        scheduler.stop()
        sys.exit(1)