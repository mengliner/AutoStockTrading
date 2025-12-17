'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-16 15:08:40
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-17 10:00:35
FilePath: \AutoStockTrading\api\task_arouter.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# api/task_router.py
from fastapi import APIRouter, Depends, HTTPException
from utils.task_manager import task_manager
from api.auth import get_current_user  # 沿用现有权限验证
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from utils.scheduler import scheduler
from db.mysql_client import MySQLClient
from db.scheduler_client import SchedulerJobClient
import json
# 路由初始化（与现有stock_router、user_router保持一致）
router = APIRouter(prefix="/api/task", tags=["任务管理"])


# 数据模型
class JobCreate(BaseModel):
    job_id: str
    job_name: str
    job_handler: str  # 任务处理函数路径
    cron_expression: str
    job_params: Optional[Dict] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_enabled: bool = True

class JobUpdate(BaseModel):
    job_name: Optional[str] = None
    job_handler: Optional[str] = None
    cron_expression: Optional[str] = None
    job_params: Optional[Dict] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_enabled: Optional[bool] = None


@router.post("/run/{task_name}", response_model=Dict[str, Any])
def run_task_manually(
    task_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    手动触发任务（仅管理员可操作）
    :param task_name: 任务名称（如：sync_yesterday_daily_k）
    """
    # 权限校验（沿用现有角色控制）
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="❌ 权限不足：仅管理员可手动触发任务")
    
    try:
        task_id = task_manager.run_task(task_name)
        return {"code": 200, "message": "✅ 任务已触发", "data": {"task_id": task_id}}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{task_id}", response_model=Dict[str, Any])
def get_task_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """查询单个任务的执行状态"""
    task_record = task_manager.get_task_record(task_id)
    if not task_record:
        raise HTTPException(status_code=404, detail=f"❌ 任务记录不存在：{task_id}")
    return {"code": 200, "data": task_record.to_dict()}

@router.get("/running", response_model=Dict[str, Any])
def get_running_tasks(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """查询所有正在运行的任务"""
    running_tasks = task_manager.get_running_tasks()
    data = [
        {"task_name": name, "task_id": task_id}
        for name, task_id in running_tasks.items()
    ]
    return {"code": 200, "data": data, "count": len(data)}



# 新增定时任务管理接口
@router.post("/scheduler/jobs", response_model=Dict[str, Any])
def create_scheduler_job(
    job: JobCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """创建定时任务"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    with MySQLClient() as db:
        client = SchedulerJobClient(db)
        if client.get_job_by_id(job.job_id):
            raise HTTPException(status_code=400, detail=f"任务ID已存在: {job.job_id}")
        
        success = client.create_job(job.dict())
        if success:
            scheduler.refresh_jobs()  # 刷新任务
            return {"code": 200, "message": "定时任务创建成功"}
        raise HTTPException(status_code=500, detail="创建任务失败")

@router.put("/scheduler/jobs/{job_id}", response_model=Dict[str, Any])
def update_scheduler_job(
    job_id: str,
    job: JobUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """更新定时任务"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    with MySQLClient() as db:
        client = SchedulerJobClient(db)
        if not client.get_job_by_id(job_id):
            raise HTTPException(status_code=404, detail=f"任务不存在: {job_id}")
        
        success = client.update_job(job_id, job.dict(exclude_unset=True))
        if success:
            scheduler.refresh_jobs()  # 刷新任务
            return {"code": 200, "message": "定时任务更新成功"}
        raise HTTPException(status_code=500, detail="更新任务失败")

@router.delete("/scheduler/jobs/{job_id}", response_model=Dict[str, Any])
def delete_scheduler_job(
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """删除定时任务"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    with MySQLClient() as db:
        client = SchedulerJobClient(db)
        if not client.get_job_by_id(job_id):
            raise HTTPException(status_code=404, detail=f"任务不存在: {job_id}")
        
        success = client.delete_job(job_id)
        if success:
            scheduler.refresh_jobs()  # 刷新任务
            return {"code": 200, "message": "定时任务删除成功"}
        raise HTTPException(status_code=500, detail="删除任务失败")

@router.get("/scheduler/jobs", response_model=Dict[str, Any])
def get_all_scheduler_jobs(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """查询所有定时任务配置"""
    with MySQLClient() as db:
        client = SchedulerJobClient(db)
        jobs = client.get_all_jobs()  # 查询所有任务（包括禁用的）
        return {"code": 200, "data": jobs}