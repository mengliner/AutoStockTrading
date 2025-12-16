'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-16 15:08:40
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-16 15:34:03
FilePath: \AutoStockTrading\api\task_arouter.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# api/task_router.py
from fastapi import APIRouter, Depends, HTTPException
from utils.task_manager import task_manager
from api.auth import get_current_user  # 沿用现有权限验证
from typing import Dict, Any

# 路由初始化（与现有stock_router、user_router保持一致）
router = APIRouter(prefix="/api/task", tags=["任务管理"])

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