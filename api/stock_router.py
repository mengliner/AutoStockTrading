'''
Author: mengliner 1219948661@qq.com
Date: 2025-12-15 16:22:47
LastEditors: mengliner 1219948661@qq.com
LastEditTime: 2025-12-16 00:48:13
FilePath: \AutoStockTrading\api\stock_router.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from fastapi import APIRouter, Depends, HTTPException
from db.mysql_client import MySQLClient
from api.auth import get_current_user

router = APIRouter(prefix="/api/stock")

@router.get("/basic",summary="获取股票基础信息列表")
def get_stock_basic(page: int = 1, page_size: int = 20, user=Depends(get_current_user)):
    with MySQLClient() as db:
        return db.query_paginate("SELECT * FROM stock_basic", page, page_size)

@router.get("/kline/{ts_code}")
def get_stock_kline(ts_code: str, start_date: str, end_date: str, user=Depends(get_current_user)):
    with MySQLClient() as db:
        return db.query_all(
            "SELECT * FROM daily_k WHERE ts_code=%s AND trade_date BETWEEN %s AND %s",
            (ts_code, start_date, end_date)
        )

@router.post("/favorite/{ts_code}")
def add_favorite(ts_code: str, user=Depends(get_current_user)):
    with MySQLClient() as db:
        if db.add_favorite(user["id"], ts_code):
            return {"message": "收藏成功"}
        raise HTTPException(status_code=400, detail="已收藏或操作失败")

@router.delete("/favorite/{ts_code}")
def remove_favorite(ts_code: str, user=Depends(get_current_user)):
    with MySQLClient() as db:
        if db.remove_favorite(user["id"], ts_code):
            return {"message": "取消收藏成功"}
        raise HTTPException(status_code=400, detail="未收藏或操作失败")

@router.get("/favorites")
def get_favorites(user=Depends(get_current_user)):
    with MySQLClient() as db:
        favorites = db.get_user_favorites(user["id"])
        ts_codes = [f["ts_code"] for f in favorites]
        if not ts_codes:
            return {"data": []}
        # 查询收藏的股票详情
        placeholders = ", ".join(["%s"] * len(ts_codes))
        return db.query_all(f"SELECT * FROM stock_basic WHERE ts_code IN ({placeholders})", tuple(ts_codes))