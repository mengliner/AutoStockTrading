import pandas as pd
import os
from utils.log_utils import logger  # 复用日志工具（若无则用print替代）

class CSVClient:
    def __init__(self):
        self.supported_formats = ['.csv']  # 支持的文件格式

    def _check_file(self, file_path: str) -> bool:
        """检查文件是否存在且格式合法"""
        if not os.path.exists(file_path):
            logger.error(f"CSV文件不存在：{file_path}")
            return False
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            logger.error(f"不支持的文件格式：{file_ext}，仅支持{self.supported_formats}")
            return False
        return True

    def read_stock_csv(self, file_path: str, table_type: str = "stock_basic") -> pd.DataFrame:
        """
        读取股票CSV文件并标准化数据
        :param file_path: CSV文件路径
        :param table_type: 数据类型（daily_k/stock_basic），用于适配字段清洗
        :return: 标准化后的DataFrame
        """
        # 1. 检查文件
        if not self._check_file(file_path):
            return pd.DataFrame()
        
        # 2. 读取CSV（自动处理编码/分隔符）
        try:
            # 尝试不同编码读取（解决中文乱码）
            encodings = ['utf-8', 'gbk', 'gb2312']
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        dtype=str  # 先统一按字符串读取，避免类型错误
                    )
                    break
                except Exception:
                    continue
            if df is None:
                logger.error(f"无法读取CSV文件（所有编码尝试失败）：{file_path}")
                return pd.DataFrame()
            
            logger.info(f"成功读取CSV文件：{file_path}，共{len(df)}行数据")

            # 3. 数据标准化（适配MySQL表结构）
            df = self._clean_data(df, table_type)
            return df

        except Exception as e:
            logger.error(f"读取CSV文件失败：{e}")
            return pd.DataFrame()

    def _clean_data(self, df: pd.DataFrame, table_type: str) -> pd.DataFrame:
        """根据表类型清洗数据，适配MySQL字段"""
        # 空值填充
        df = df.fillna("" if table_type == "stock_basic" else 0)

        # 字段名映射（解决CSV字段名与数据库不一致问题）
        field_maps = {
            "daily_k": {
                "股票代码": "ts_code",
                "交易日期": "trade_date",
                "开盘价": "open",
                "最高价": "high",
                "最低价": "low",
                "收盘价": "close",
                "昨收价": "pre_close",
                "涨跌额": "change_amt",  # 对应修改后的MySQL字段（规避change关键字）
                "涨跌幅": "pct_chg",
                "成交量": "vol",
                "成交额": "amount"
            },
            "stock_basic": {
                "TS代码": "ts_code",
                "股票代码": "symbol",
                "股票名称": "name",
                "地域" :"area",
                "所属行业" :"industry",
                "股票全称" :"fullname",
                "英文全称" :"enname",
                "拼音缩写" :"cnspell",
                "市场类型" :"market",
                "交易所代码" :"exchange",
                "交易货币" :"curr_type",
                "上市状态" :"list_status",
                "上市日期" :"list_date",
                "退市日期" :"delist_date",
                "是否沪深港通标的":"is_hs",
                "实控人名称" :"act_name",
                "实控人企业性质" :"act_ent_type",
            }
        }

        # 重命名字段（兼容自定义CSV字段名）
        df.rename(columns=field_maps.get(table_type, {}), inplace=True)

        # 类型转换（适配MySQL字段类型）
        if table_type == "daily_k":
            # 数值字段转浮点型
            num_fields = ["open", "high", "low", "close", "pre_close", "change_amt", "pct_chg", "vol", "amount"]
            for field in num_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)
            # 日期字段标准化
            if "trade_date" in df.columns:
                df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce").dt.date

        elif table_type == "stock_basic":
            # 日期字段标准化
            if "list_date" in df.columns:
                df["list_date"] = pd.to_datetime(df["list_date"], errors="coerce").dt.date
            if "delist_date" in df.columns:
                df["delist_date"] = pd.to_datetime(df["delist_date"], errors="coerce").dt.date

        # 过滤必要字段（仅保留MySQL表中存在的字段）
        table_fields = {
            "daily_k": ["ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "change_amt", "pct_chg", "vol", "amount"],
            "stock_basic": ["ts_code","symbol","name","area","industry","fullname","enname","cnspell","market","exchange","curr_type","list_status","list_date","delist_date","is_hs","act_name","act_ent_type"]
        }
        df = df[[f for f in table_fields[table_type] if f in df.columns]]
        return df