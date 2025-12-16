'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-13 14:44:28
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-16 15:44:11
FilePath: \AutoStockTrading\db\__init__.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
STOCK_BASIC_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS stock_basic (
    ts_code VARCHAR(20) PRIMARY KEY,  # 股票代码（如000001.SZ）
    symbol VARCHAR(10) NOT NULL,     # 股票代码（纯数字）
    name VARCHAR(50) NOT NULL,       # 股票名称
    industry VARCHAR(50),            # 所属行业
    list_date DATE                   # 上市日期
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

DAILY_K_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS daily_k (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ts_code VARCHAR(20) NOT NULL,    # 股票代码
    trade_date DATE NOT NULL,        # 交易日期
    open FLOAT NOT NULL,             # 开盘价
    high FLOAT NOT NULL,             # 最高价
    low FLOAT NOT NULL,              # 最低价
    close FLOAT NOT NULL,            # 收盘价
    pre_close FLOAT NOT NULL,        # 昨收价
    change_value FLOAT NOT NULL,           # 涨跌额
    pct_chg FLOAT NOT NULL,          # 涨跌幅
    vol FLOAT NOT NULL,              # 成交量（手）
    amount FLOAT NOT NULL,           # 成交额（千元）
    UNIQUE KEY idx_ts_date (ts_code, trade_date)  # 唯一索引（避免重复）
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""


# 用户表
USER_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user (
    id VARCHAR(32) PRIMARY KEY, 
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

# 新增收藏表

FAVORITE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS favorite (
    id VARCHAR(32) PRIMARY KEY,  
    user_id VARCHAR(32) NOT NULL,   
    ts_code VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),  
    UNIQUE KEY uk_user_stock (user_id, ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""


# 任务记录表SQL（已在之前创建，此处仅保留代码供参考）
TASK_RECORD_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS task_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(50) UNIQUE NOT NULL COMMENT '任务唯一ID',
    task_name VARCHAR(50) NOT NULL COMMENT '任务名称',
    start_time DATETIME NOT NULL COMMENT '任务开始时间',
    end_time DATETIME COMMENT '任务结束时间',
    status VARCHAR(20) NOT NULL COMMENT '任务状态：pending/running/completed/failed',
    error_msg TEXT COMMENT '任务失败错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='定时任务执行记录表';
"""

def create_all_tables(mysql_client):
    """
    统一创建所有数据表（供外部调用）
    :param mysql_client: MySQLClient实例
    """
    try:
        mysql_client.create_table("stock_basic", STOCK_BASIC_TABLE_SQL)
        mysql_client.create_table("daily_k", DAILY_K_TABLE_SQL)
        mysql_client.create_table("user", USER_TABLE_SQL)
        mysql_client.create_table("favorite", FAVORITE_TABLE_SQL)
        mysql_client.create_table("task_record", TASK_RECORD_TABLE_SQL)
        print("✅ 所有数据表创建/检查完成")
    except Exception as e:
        raise Exception(f"❌ 创建数据表失败: {e}")