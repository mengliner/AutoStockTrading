'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-17 09:33:18
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-17 09:33:29
FilePath: \AutoStockTrading\service\stock_task_service.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from data.tushare_client import TushareClient
from db.mysql_client import MySQLClient
from utils.log_utils import logger

tushare_client = TushareClient()

def fetch_stock_basic():
    """获取股票基础信息（可被定时任务调用）"""
    try:
        df = tushare_client.get_stock_basic()
        with MySQLClient() as db:
            db.insert_data("stock_basic", df)
        logger.info("股票基础信息定时更新完成")
    except Exception as e:
        logger.error(f"股票基础信息更新失败: {str(e)}")

def fetch_daily_k(**kwargs):
    """获取日K线数据（可被定时任务调用）"""
    try:
        ts_code = kwargs.get("ts_code")
        if not ts_code:
            raise Exception("缺少股票代码参数")
            
        df = tushare_client.get_daily_k_data(
            ts_code=ts_code,
            start_date=kwargs.get("start_date", "20230101"),
            end_date=kwargs.get("end_date", "20231231")
        )
        with MySQLClient() as db:
            db.insert_data("daily_k", df)
        logger.info(f"{ts_code} 日K线数据定时更新完成")
    except Exception as e:
        logger.error(f"日K线数据更新失败: {str(e)}")