'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-16 15:09:57
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-16 15:10:49
FilePath: \AutoStockTrading\service\daily_k_service.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# service/daily_k_service.py
import time
from datetime import datetime, timedelta
from db.mysql_client import MySQLClient
from data.tushare_client import TushareClient  # 沿用现有Tushare客户端
from utils.log_utils import logger

def sync_yesterday_daily_k():
    """核心任务：检查并同步前一天股票日K数据"""
    # 1. 计算日期（格式：YYYYMMDD）
    today = datetime.now().strftime("%Y%m%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    logger.info(f"📊 开始执行前一日日K同步任务：今日{today}，同步{yesterday}的数据")

    # 2. 初始化客户端
    tushare_client = TushareClient()

    # 3. 数据库操作：检查是否已同步 + 执行同步
    with MySQLClient() as db:
        # 3.1 检查是否已同步（避免重复拉取）
        count = db.query_one(
            "SELECT COUNT(*) AS cnt FROM daily_k WHERE trade_date = %s",
            (yesterday,)
        )["cnt"]
        if count > 0:
            logger.info(f"✅ {yesterday}的日K数据已同步（共{count}条），无需重复执行")
            return

        # 3.2 获取需要同步的股票列表（沿用现有股票基础表）
        ts_codes = db.query_all(
            "SELECT ts_code FROM stock_basic WHERE market NOT IN (%s, %s)",
            ("创业板", "科创板")  # 可根据需求调整
        )
        ts_codes = [item["ts_code"] for item in ts_codes]
        logger.info(f"📋 共需同步{len(ts_codes)}只股票的{yesterday}日K数据")

        # 3.3 批量同步数据（控制Tushare API调用频率）
        success_cnt = 0
        fail_cnt = 0
        for ts_code in ts_codes:
            try:
                # 调用Tushare获取单只股票日K数据
                df = tushare_client.get_daily_k_data(
                    ts_code=ts_code, start_date=yesterday, end_date=yesterday
                )
                if not df.empty:
                    # 插入数据库（沿用现有插入方法）
                    db.insert_data("daily_k", df)
                    success_cnt += 1
                else:
                    logger.warning(f"⚠️ {ts_code}在{yesterday}无交易数据")
                time.sleep(1.2)  # 控制API频率，避免触发限流
            except Exception as e:
                fail_cnt += 1
                logger.error(f"❌ 同步{ts_code}失败：{str(e)}")

        # 3.4 任务结束日志
        logger.info(
            f"📊 {yesterday}日K同步任务完成："
            f"成功{success_cnt}只 | 失败{fail_cnt}只 | 总计{len(ts_codes)}只"
        )