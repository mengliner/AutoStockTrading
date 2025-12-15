import pymysql
import pandas as pd
from pymysql import Error
from typing import List, Dict, Tuple, Optional, Any
from config.db_config import DB_CONFIG
from utils.log_utils import logger

class MySQLClient:

    def __init__(self):
        self.config = DB_CONFIG
        self.connection = None
        self.cursor = None
        # 初始化时创建数据库（若不存在）
        self._create_database_if_not_exists()

    def _create_database_if_not_exists(self):
        """创建数据库（先连接无db，创建后再重连）"""
        temp_config = self.config.copy()
        temp_config.pop("database")
        try:
            conn = pymysql.connect(** temp_config)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']} DEFAULT CHARSET {self.config['charset']}")
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            raise Exception(f"创建数据库失败: {e}")

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                **self.config,
                autocommit=True,  # 自动提交事务
                cursorclass=pymysql.cursors.DictCursor  # 返回字典格式结果
            )
            self.cursor = self.connection.cursor()
            print("✅ MySQL连接成功（8.0.11）")
        except Error as e:
            raise Exception(f"MySQL连接失败: {e}")

    def create_table(self, table_name: str, create_sql: str):
        """创建数据表"""
        try:
            self.cursor.execute(create_sql)
            print(f"✅ 表{table_name}创建/存在成功")
        except Error as e:
            raise Exception(f"创建表{table_name}失败: {e}")

    def insert_data(self, table_name: str, df: pd.DataFrame):
        """批量插入DataFrame数据到MySQL"""
        if df.empty:
            print("⚠️ 无数据可插入")
            logger.warning(f"⚠️ 无数据可插入到{table_name}（CSV文件可能为空或格式错误）")  # 替换print为日志（若无日志则保留print）
            return
        
        # 获取列名和占位符
        columns = df.columns.tolist()
        #print(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        #print(insert_sql)
        # 转换DataFrame为元组列表
        data = [tuple(row) for row in df.values]
        
        try:
            # 批量执行（提高效率）
            self.cursor.executemany(insert_sql, data)
            print(f"✅ 成功插入{len(data)}条数据到{table_name}")
        except Error as e:
            self.connection.rollback()
            raise Exception(f"插入数据失败: {e}")

    def close(self):
        """关闭连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 MySQL连接已关闭")

    def __enter__(self):
        """上下文管理器：自动连接"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器：自动关闭"""
        self.close()

    # -------------------------- 基础CRUD操作 --------------------------
    def execute(self, sql: str, params: Optional[Tuple] = None) -> int:
        """
        执行单条SQL（增/删/改）
        :param sql: SQL语句（支持占位符%s）
        :param params: SQL参数（元组）
        :return: 受影响行数
        """
        try:
            affected_rows = self.cursor.execute(sql, params or ())
            self.connection.commit()
            print(f"✅ SQL执行成功，受影响行数: {affected_rows}")
            return affected_rows
        except Error as e:
            self.connection.rollback()
            raise Exception(f"❌ SQL执行失败: {e} | SQL: {sql} | 参数: {params}")

    def query_one(self, sql: str, params: Optional[Tuple] = None) -> Optional[Dict]:
        """
        查询单条数据
        :param sql: 查询SQL
        :param params: 查询参数
        :return: 单条数据（字典格式）| None
        """
        try:
            self.cursor.execute(sql, params or ())
            result = self.cursor.fetchone()
            print(f"✅ 查询到{1 if result else 0}条数据")
            return result
        except Error as e:
            raise Exception(f"❌ 查询失败: {e} | SQL: {sql} | 参数: {params}")

    def query_all(self, sql: str, params: Optional[Tuple] = None) -> List[Dict]:
        """
        查询多条数据
        :param sql: 查询SQL
        :param params: 查询参数
        :return: 多条数据（字典列表）
        """
        try:
            self.cursor.execute(sql, params or ())
            result = self.cursor.fetchall()
            print(f"✅ 查询到{len(result)}条数据")
            return result
        except Error as e:
            raise Exception(f"❌ 查询失败: {e} | SQL: {sql} | 参数: {params}")

    def query_paginate(self, sql: str, page: int = 1, page_size: int = 10, params: Optional[Tuple] = None) -> Dict:
        """
        分页查询
        :param sql: 查询SQL（不含LIMIT）
        :param page: 页码（从1开始）
        :param page_size: 每页条数
        :param params: 查询参数
        :return: {"total": 总数, "data": 分页数据, "page": 当前页, "page_size": 每页条数}
        """
        try:
            # 先查总数
            count_sql = f"SELECT COUNT(*) as total FROM ({sql}) as temp"
            self.cursor.execute(count_sql, params or ())
            total = self.cursor.fetchone()["total"]
            
            # 分页查询数据
            offset = (page - 1) * page_size
            paginate_sql = f"{sql} LIMIT {offset}, {page_size}"
            self.cursor.execute(paginate_sql, params or ())
            data = self.cursor.fetchall()
            
            result = {
                "total": total,
                "data": data,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size  # 总页数
            }
            print(f"✅ 分页查询完成：第{page}页/共{result['pages']}页，总计{total}条")
            return result
        except Error as e:
            raise Exception(f"❌ 分页查询失败: {e} | SQL: {sql} | 参数: {params}")

    # -------------------------- 批量操作 --------------------------
    def batch_execute(self, sql: str, params_list: List[Tuple]) -> int:
        """
        批量执行SQL（如批量插入/更新/删除）
        :param sql: SQL语句（支持占位符%s）
        :param params_list: 参数列表（元组列表）
        :return: 受影响总行数
        """
        if not params_list:
            print("⚠️ 批量执行无参数，跳过")
            return 0
        try:
            affected_rows = self.cursor.executemany(sql, params_list)
            self.connection.commit()
            print(f"✅ 批量执行成功，总计受影响行数: {affected_rows}")
            return affected_rows
        except Error as e:
            self.connection.rollback()
            raise Exception(f"❌ 批量执行失败: {e} | SQL: {sql} | 参数数量: {len(params_list)}")

    def insert_data(self, table_name: str, df: pd.DataFrame, batch_size: int = 1000) -> int:
        """
        批量插入DataFrame数据（优化大文件插入性能）
        :param table_name: 表名
        :param df: 待插入的DataFrame
        :param batch_size: 每批插入条数
        :return: 总插入行数
        """
        if df.empty:
            print("⚠️ 无数据可插入")
            return 0
        
        # 空值填充（字符串填空，数值填0）
        df = df.fillna("").replace({pd.NA: "", None: ""})
        # 过滤表中不存在的列
        self.cursor.execute(f"DESCRIBE {table_name}")
        table_columns = [col["Field"] for col in self.cursor.fetchall()]
        df = df[[col for col in df.columns if col in table_columns]]
        
        if df.empty:
            raise Exception(f"❌ DataFrame无匹配的表字段，表字段: {table_columns}")
        
        # 构建插入SQL
        columns = df.columns.tolist()
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"INSERT IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # 转换DataFrame为元组列表
        data = [tuple(row) for row in df.values]
        total_inserted = 0
        
        try:
            # 分批次插入
            for i in range(0, len(data), batch_size):
                batch = data[i:i+batch_size]
                affected = self.cursor.executemany(insert_sql, batch)
                total_inserted += affected
                self.connection.commit()
                print(f"✅ 批次{i//batch_size + 1}插入完成，插入{affected}条")
            
            print(f"✅ 全部插入完成，总计插入{total_inserted}条数据到{table_name}")
            return total_inserted
        except Error as e:
            self.connection.rollback()
            raise Exception(f"❌ 批量插入失败: {e} | 表名: {table_name} | 批次: {i//batch_size + 1}")

    # -------------------------- 表操作 --------------------------
    def create_table(self, table_name: str, create_sql: str) -> bool:
        """
        创建数据表（支持IF NOT EXISTS）
        :param table_name: 表名
        :param create_sql: 创建表的SQL语句
        :return: 创建结果（True/False）
        """
        try:
            self.cursor.execute(create_sql)
            self.connection.commit()
            print(f"✅ 表{table_name}创建/已存在")
            return True
        except Error as e:
            self.connection.rollback()

    # 新增用户相关方法
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        sql = "SELECT * FROM user WHERE username = %s"
        return self.query_one(sql, (username,))

    def create_user(self, username: str, password_hash: str) -> bool:
        sql = "INSERT INTO user (username, password_hash) VALUES (%s, %s)"
        return self.execute(sql, (username, password_hash)) > 0

    # 新增收藏相关方法
    def add_favorite(self, user_id: int, ts_code: str) -> bool:
        sql = "INSERT IGNORE INTO favorite (user_id, ts_code) VALUES (%s, %s)"
        return self.execute(sql, (user_id, ts_code)) > 0

    def remove_favorite(self, user_id: int, ts_code: str) -> bool:
        sql = "DELETE FROM favorite WHERE user_id = %s AND ts_code = %s"
        return self.execute(sql, (user_id, ts_code)) > 0

    def get_user_favorites(self, user_id: int) -> List[Dict]:
        sql = "SELECT ts_code FROM favorite WHERE user_id = %s"
        return self.query_all(sql, (user_id,))