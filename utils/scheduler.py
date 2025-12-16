# utils/scheduler.py
# -*- coding: utf-8 -*-
import time
import threading
from utils.log_utils import logger
from utils.task_manager import task_manager

class Scheduler:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.init()
        return cls._instance

    def init(self):
        self.jobs = []
        self.running = False
        self.thread = None

    def add_job(self, task_name: str, interval: int, *args, **kwargs):
        self.jobs.append({
            "task_name": task_name,
            "interval": interval,
            "last_run": None,
            "args": args,
            "kwargs": kwargs
        })
        logger.info(f"⏰ 定时任务添加成功：{task_name}（间隔：{interval}秒）")

    def start(self):
        if self.running:
            logger.warning("⚠️ 调度器已在运行，无需重复启动")
            return
        self.running = True
        # 非守护线程：避免主线程退出时被强制终止（关键修改）
        self.thread = threading.Thread(target=self._schedule_loop, daemon=False)
        self.thread.start()
        logger.info("✅ 调度器启动成功")

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)  # 等待5秒，确保线程退出
        logger.info("🛑 调度器已停止")

    def _schedule_loop(self):
        """调度循环：持续运行直到收到停止信号"""
        while self.running:
            now = time.time()
            for job in self.jobs:
                if job["last_run"] is None or (now - job["last_run"] >= job["interval"]):
                    try:
                        task_id = task_manager.run_task(
                            job["task_name"], *job["args"], **job["kwargs"]
                        )
                        job["last_run"] = now
                        logger.info(f"⏰ 定时任务触发：{job['task_name']}（任务ID：{task_id}）")
                    except Exception as e:
                        logger.error(f"❌ 定时任务调度失败：{job['task_name']}，错误：{str(e)}")
            time.sleep(10)  # 每10秒检查一次
        logger.info("📌 调度器循环已退出")