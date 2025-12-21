# service/daily_k_service.py
import time
from datetime import datetime, timedelta
from db.mysql_client import MySQLClient
from data.tushare_client import TushareClient
from utils.log_utils import logger
from typing import Optional, List

def sync_daily_k_data(
    ts_codes: Optional[List[str]] = None,  # 支持多股票代码列表
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    同步股票日K数据（支持多股票批量同步）
    :param ts_codes: 股票代码列表（如：["000001.SZ", "600000.SH"]，None表示所有股票）
    :param start_date: 开始日期（格式：YYYYMMDD，None默认前一天）
    :param end_date: 结束日期（格式：YYYYMMDD，None默认前一天）
    """
    # 1. 日期处理（默认前一天）
    today = datetime.now().strftime("%Y%m%d")
    default_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    start_date = start_date or default_date
    end_date = end_date or default_date
    
    logger.info(
        f"📊 开始执行日K同步任务："
        f"股票代码={ts_codes or '所有'}，"
        f"日期范围={start_date}至{end_date}"
    )

    # 2. 初始化客户端
    tushare_client = TushareClient()

    # 3. 数据库操作
    with MySQLClient() as db:
        # 3.1 区分处理：全量同步/指定股票同步
        try:
            if not ts_codes:
                # 全量同步：不传入ts_code，利用Tushare批量接口
                logger.info(f"📥 开始批量获取所有股票{start_date}-{end_date}日K数据")
                df = tushare_client.get_daily_k_data(
                    ts_code=None,  # 关键：不传股票代码，Tushare返回全量数据
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not df.empty:
                    # 按股票代码分组删除旧数据（避免重复）
                    unique_codes = df['ts_code'].unique()
                    for code in unique_codes:
                        db.execute(
                            "DELETE FROM daily_k WHERE ts_code = %s AND trade_date BETWEEN %s AND %s",
                            (code, start_date, end_date)
                        )
                    # 批量插入全量数据
                    db.insert_data("daily_k", df)
                    logger.info(f"✅ 全量同步完成，共{len(df)}条数据")
                else:
                    logger.warning(f"⚠️ {start_date}-{end_date}无全量日K数据")

            else:
                # 指定股票同步（支持单只/多只）
                logger.info(f"📋 共需同步{len(ts_codes)}只股票的{start_date}-{end_date}日K数据")
                success_cnt = 0
                fail_cnt = 0
                
                for code in ts_codes:
                    try:
                        df = tushare_client.get_daily_k_data(
                            ts_code=code,
                            start_date=start_date,
                            end_date=end_date
                        )
                        
                        if not df.empty:
                            # 删除该股票指定日期数据
                            db.execute(
                                "DELETE FROM daily_k WHERE ts_code = %s AND trade_date BETWEEN %s AND %s",
                                (code, start_date, end_date)
                            )
                            db.insert_data("daily_k", df)
                            success_cnt += 1
                        else:
                            logger.warning(f"⚠️ {code}在{start_date}-{end_date}无交易数据")
                        
                        time.sleep(1.2)  # 控制单只股票API调用频率
                    except Exception as e:
                        fail_cnt += 1
                        logger.error(f"❌ 同步{code}失败：{str(e)}")
                
                logger.info(
                    f"📊 指定股票同步完成："
                    f"成功{success_cnt}只 | 失败{fail_cnt}只 | 总计{len(ts_codes)}只"
                )

        except Exception as e:
            logger.error(f"❌ 日K同步任务整体失败：{str(e)}", exc_info=True)

# 保留原定时任务接口兼容性
def sync_yesterday_daily_k():
    """兼容旧的定时任务配置，默认同步前一天所有股票数据"""
    sync_daily_k_data()