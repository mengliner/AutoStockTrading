# utils/scheduler.py
# -*- coding: utf-8 -*-
from utils.log_utils import logger
from apscheduler.schedulers.background import BackgroundScheduler
from db.mysql_client import MySQLClient
from db.scheduler_client import SchedulerJobClient
import logging
import importlib
import json
from typing import Dict

class DatabaseScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.load_jobs_from_db()

    def load_jobs_from_db(self):
        """从数据库加载所有启用的任务"""
        with MySQLClient() as db:
            job_client = SchedulerJobClient(db)
            jobs = job_client.get_enabled_jobs()
            
            for job in jobs:
                self.add_job_to_scheduler(job)

    def add_job_to_scheduler(self, job: Dict):
        """将数据库任务添加到调度器（通过反射解耦业务）"""
        try:
            # 解析任务处理函数（格式：模块路径.函数名）
            handler_path = job["job_handler"]
            module_name, func_name = handler_path.rsplit('.', 1)
            
            # 动态导入模块和函数
            module = importlib.import_module(module_name)
            func = getattr(module, func_name)
            if not callable(func):
                raise Exception(f"{handler_path} 不是可调用函数")

            # 解析任务参数
            job_params = json.loads(job["job_params"]) if job["job_params"] else {}

            # 添加定时任务
            self.scheduler.add_job(
                func,
                trigger='cron',
                cron_expression=job["cron_expression"],
                id=job["job_id"],
                name=job["job_name"],
                kwargs=job_params,
                start_date=job["start_date"],
                end_date=job["end_date"],
                replace_existing=True
            )
            logger.info(f"已加载任务: {job['job_name']} ({job['job_id']}) -> {handler_path}")
        except Exception as e:
            logger.error(f"加载任务失败 {job['job_id']}: {str(e)}")

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("定时任务调度器已启动")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("定时任务调度器已关闭")

    def refresh_jobs(self):
        """刷新任务（用于配置变更后）"""
        self.scheduler.remove_all_jobs()
        self.load_jobs_from_db()
        logger.info("定时任务已刷新")

# 全局调度器实例
scheduler = DatabaseScheduler()