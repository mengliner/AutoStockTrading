'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-13 14:45:21
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-13 17:00:04
FilePath: \AutoStockTrading\data\tushare_client.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import tushare as ts
import pandas as pd
from config.db_config import TUSHARE_CONFIG

class TushareClient:
    def __init__(self):
        # 初始化Tushare
        ts.set_token(TUSHARE_CONFIG["token"])
        tk=ts.get_token()
        self.pro = ts.pro_api()
        print("✅ Tushare初始化成功")
        print(f"token: {tk}")


    def get_stock_basic(self) -> pd.DataFrame:
        """获取股票基础信息（沪深A股）"""
        try:
            df = self.pro.stock_basic(
                exchange="",
                list_status="L",  # 上市状态：L上市 D退市 P暂停上市
                fields="ts_code,symbol,name,industry,list_date"
            )
            # 数据清洗（适配MySQL字段）
            df = df.fillna("")  # 空值填充
            df["list_date"] = pd.to_datetime(df["list_date"], errors="coerce").dt.date  # 日期格式标准化
            return df
        except Exception as e:
            raise Exception(f"获取股票基础信息失败: {e}")

    def get_daily_k_data(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取个股日K线数据"""
        try:
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            df = df.fillna(0)  # 数值字段空值填0
            # 转换日期格式
            df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce").dt.date
            df.rename(columns={'change': 'change_value'}, inplace=True)
            return df
        except Exception as e:
            raise Exception(f"获取{ts_code}日K数据失败: {e}")