'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-13 14:45:33
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-15 16:46:26
FilePath: \AutoStockTrading\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''













from db.mysql_client import MySQLClient
from data.tushare_client import TushareClient
from data.csv_client import CSVClient  # 新增导入
from utils.log_utils import logger  # 日志工具（若无则注释）
import time


def main():
    # 1. 初始化客户端
    tushare_client = TushareClient()
    mysql_client = MySQLClient()
    csv_client = CSVClient()
    start_date_test="20100101",
    end_date_test="20251212"
    try:
        # 2. 连接MySQL并创建表
        with mysql_client as db:

            # 1. 读取并清洗CSV数据
            csv_path="F:\Download\\tushare_stock_basic_20251215134515.csv"
            df = csv_client.read_stock_csv(csv_path, "stock_basic")
            db.insert_data("stock_basic", df)
            logger.info(f"✅ CSV数据写入stock_basic完成（文件：{csv_path}）")  # 无日志则用print
            
            select_sql="SELECT ts_code FROM stock_basic where market not in (%s,%s)"
            ts_code_list=db.query_all(select_sql,("创业板","科创板"))
            #print(ts_code_list)

            # for ts in  ts_code_list:
            #     daily_k_df = tushare_client.get_daily_k_data(
            #         ts_code=ts["ts_code"],
            #         start_date="19780101",
            #         end_date="20100101"
            #     )
            #     db.insert_data("daily_k", daily_k_df)
            #     logger.info(ts["ts_code"]+"数据已处理完成")
            #     time.sleep(1.2)
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")

if __name__ == "__main__":
    main()