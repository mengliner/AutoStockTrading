
#### 二、定时任务数据库操作层
新建 `db/scheduler_client.py`
```python
from typing import List, Dict, Optional
from db.mysql_client import MySQLClient
import json

class SchedulerJobClient:
    def __init__(self, mysql_client: MySQLClient):
        self.db = mysql_client

    def get_enabled_jobs(self) -> List[Dict]:
        """查询所有启用的定时任务"""
        sql = """
        SELECT id, job_id, job_name, job_handler, cron_expression, 
               job_params, start_date, end_date, is_enabled
        FROM scheduler_job 
        WHERE is_enabled = TRUE
        """
        return self.db.query_all(sql)

    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """通过job_id查询任务"""
        sql = """
        SELECT id, job_id, job_name, job_handler, cron_expression, 
               job_params, start_date, end_date, is_enabled
        FROM scheduler_job 
        WHERE job_id = %s
        """
        return self.db.query_one(sql, (job_id,))

    def create_job(self, job_data: Dict) -> bool:
        """创建新任务"""
        sql = """
        INSERT INTO scheduler_job (
            job_id, job_name, job_handler, cron_expression, 
            job_params, start_date, end_date, is_enabled
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        job_params = json.dumps(job_data.get("job_params")) if job_data.get("job_params") else None
        params = (
            job_data["job_id"],
            job_data["job_name"],
            job_data["job_handler"],
            job_data["cron_expression"],
            job_params,
            job_data.get("start_date"),
            job_data.get("end_date"),
            job_data.get("is_enabled", True)
        )
        return self.db.execute(sql, params) > 0

    def update_job(self, job_id: str, update_data: Dict) -> bool:
        """更新任务配置"""
        update_fields = []
        params = []
        if "job_name" in update_data:
            update_fields.append("job_name = %s")
            params.append(update_data["job_name"])
        if "job_handler" in update_data:
            update_fields.append("job_handler = %s")
            params.append(update_data["job_handler"])
        if "cron_expression" in update_data:
            update_fields.append("cron_expression = %s")
            params.append(update_data["cron_expression"])
        if "job_params" in update_data:
            update_fields.append("job_params = %s")
            params.append(json.dumps(update_data["job_params"]))
        if "start_date" in update_data:
            update_fields.append("start_date = %s")
            params.append(update_data["start_date"])
        if "end_date" in update_data:
            update_fields.append("end_date = %s")
            params.append(update_data["end_date"])
        if "is_enabled" in update_data:
            update_fields.append("is_enabled = %s")
            params.append(update_data["is_enabled"])
        
        if not update_fields:
            return False
        
        sql = f"UPDATE scheduler_job SET {', '.join(update_fields)} WHERE job_id = %s"
        params.append(job_id)
        return self.db.execute(sql, tuple(params)) > 0

    def delete_job(self, job_id: str) -> bool:
        """删除任务"""
        sql = "DELETE FROM scheduler_job WHERE job_id = %s"
        return self.db.execute(sql, (job_id,)) > 0