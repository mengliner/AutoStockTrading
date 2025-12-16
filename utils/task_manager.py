# utils/task_manager.py
import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, Any, Optional
from utils.log_utils import logger

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskRecord:
    def __init__(self, task_id: str, task_name: str):
        self.task_id = task_id
        self.task_name = task_name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.status = TaskStatus.PENDING
        self.error_msg: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.end_time - self.start_time if self.start_time and self.end_time else None,
            "status": self.status.value,
            "error_msg": self.error_msg
        }

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Callable] = {}  # 任务名称 -> 任务函数
        self.task_records: Dict[str, TaskRecord] = {}  # 任务ID -> 任务记录
        self.running_tasks: Dict[str, str] = {}  # 任务名称 -> 任务ID (当前运行中)
        self.lock = threading.Lock()

    def register_task(self, task_name: str, task_func: Callable):
        """注册任务"""
        self.tasks[task_name] = task_func
        logger.info(f"任务注册成功: {task_name}")

    def get_task_record(self, task_id: str) -> Optional[TaskRecord]:
        """获取任务记录"""
        return self.task_records.get(task_id)

    def get_running_task_id(self, task_name: str) -> Optional[str]:
        """获取运行中的任务ID"""
        return self.running_tasks.get(task_name)

    def is_task_running(self, task_name: str) -> bool:
        """检查任务是否正在运行"""
        return task_name in self.running_tasks

    def run_task(self, task_name: str, *args, **kwargs) -> str:
        """
        运行任务（带并发控制）
        返回任务ID
        """
        with self.lock:
            # 检查任务是否存在
            if task_name not in self.tasks:
                raise ValueError(f"任务不存在: {task_name}")
            
            # 检查是否已有相同任务在运行
            if self.is_task_running(task_name):
                running_task_id = self.get_running_task_id(task_name)
                logger.warning(f"任务{task_name}已在运行中 (任务ID: {running_task_id})，本次调用被丢弃")
                return running_task_id
            
            # 创建任务记录
            task_id = f"{task_name}_{int(time.time())}"
            task_record = TaskRecord(task_id, task_name)
            self.task_records[task_id] = task_record
            self.running_tasks[task_name] = task_id

        # 在新线程中执行任务
        def task_wrapper():
            try:
                task_record.start_time = time.time()
                task_record.status = TaskStatus.RUNNING
                logger.info(f"任务开始执行: {task_name} (任务ID: {task_id})")
                
                # 执行任务
                self.tasks[task_name](*args, **kwargs)
                
                task_record.status = TaskStatus.COMPLETED
                logger.info(f"任务执行成功: {task_name} (任务ID: {task_id})")
            except Exception as e:
                task_record.status = TaskStatus.FAILED
                task_record.error_msg = str(e)
                logger.error(f"任务执行失败: {task_name} (任务ID: {task_id})，错误: {str(e)}")
            finally:
                task_record.end_time = time.time()
                with self.lock:
                    if self.running_tasks.get(task_name) == task_id:
                        del self.running_tasks[task_name]

        threading.Thread(target=task_wrapper, daemon=True).start()
        return task_id

# 全局任务管理器实例
task_manager = TaskManager()# utils/task_manager.py
import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, Any, Optional
from utils.log_utils import logger

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskRecord:
    def __init__(self, task_id: str, task_name: str):
        self.task_id = task_id
        self.task_name = task_name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.status = TaskStatus.PENDING
        self.error_msg: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.end_time - self.start_time if self.start_time and self.end_time else None,
            "status": self.status.value,
            "error_msg": self.error_msg
        }

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Callable] = {}  # 任务名称 -> 任务函数
        self.task_records: Dict[str, TaskRecord] = {}  # 任务ID -> 任务记录
        self.running_tasks: Dict[str, str] = {}  # 任务名称 -> 任务ID (当前运行中)
        self.lock = threading.Lock()

    def register_task(self, task_name: str, task_func: Callable):
        """注册任务"""
        self.tasks[task_name] = task_func
        logger.info(f"任务注册成功: {task_name}")

    def get_task_record(self, task_id: str) -> Optional[TaskRecord]:
        """获取任务记录"""
        return self.task_records.get(task_id)

    def get_running_task_id(self, task_name: str) -> Optional[str]:
        """获取运行中的任务ID"""
        return self.running_tasks.get(task_name)

    def is_task_running(self, task_name: str) -> bool:
        """检查任务是否正在运行"""
        return task_name in self.running_tasks

    def run_task(self, task_name: str, *args, **kwargs) -> str:
        """
        运行任务（带并发控制）
        返回任务ID
        """
        with self.lock:
            # 检查任务是否存在
            if task_name not in self.tasks:
                raise ValueError(f"任务不存在: {task_name}")
            
            # 检查是否已有相同任务在运行
            if self.is_task_running(task_name):
                running_task_id = self.get_running_task_id(task_name)
                logger.warning(f"任务{task_name}已在运行中 (任务ID: {running_task_id})，本次调用被丢弃")
                return running_task_id
            
            # 创建任务记录
            task_id = f"{task_name}_{int(time.time())}"
            task_record = TaskRecord(task_id, task_name)
            self.task_records[task_id] = task_record
            self.running_tasks[task_name] = task_id

        # 在新线程中执行任务
        def task_wrapper():
            try:
                task_record.start_time = time.time()
                task_record.status = TaskStatus.RUNNING
                logger.info(f"任务开始执行: {task_name} (任务ID: {task_id})")
                
                # 执行任务
                self.tasks[task_name](*args, **kwargs)
                
                task_record.status = TaskStatus.COMPLETED
                logger.info(f"任务执行成功: {task_name} (任务ID: {task_id})")
            except Exception as e:
                task_record.status = TaskStatus.FAILED
                task_record.error_msg = str(e)
                logger.error(f"任务执行失败: {task_name} (任务ID: {task_id})，错误: {str(e)}")
            finally:
                task_record.end_time = time.time()
                with self.lock:
                    if self.running_tasks.get(task_name) == task_id:
                        del self.running_tasks[task_name]

        threading.Thread(target=task_wrapper, daemon=True).start()
        return task_id

# 全局任务管理器实例
task_manager = TaskManager()