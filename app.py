#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物流演示系统 - FastAPI 接口服务
"""

from fastapi import FastAPI, HTTPException, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import sqlite3
from datetime import datetime
import uvicorn

# 数据库路径
DB_PATH = '/home/ubuntu/logistics_demo/logistics.db'

# 创建 FastAPI 应用
app = FastAPI(
    title="物流演示系统 API",
    description="为 YCloud AI 机器人提供物流查询和预约服务的演示接口",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class TrackingRecord(BaseModel):
    """物流轨迹记录"""
    status: str = Field(..., description="状态代码")
    location: str = Field(..., description="位置")
    description: str = Field(..., description="描述")
    timestamp: str = Field(..., description="时间戳")

class OrderDetail(BaseModel):
    """订单详情"""
    order_id: str = Field(..., description="订单号")
    customer_name: str = Field(..., description="客户姓名")
    customer_phone: str = Field(..., description="客户电话")
    pickup_address: str = Field(..., description="取件地址")
    delivery_address: str = Field(..., description="配送地址")
    package_type: str = Field(..., description="包裹类型")
    status: str = Field(..., description="状态代码")
    status_text: str = Field(..., description="状态文本")
    current_location: Optional[str] = Field(None, description="当前位置")
    estimated_delivery: Optional[str] = Field(None, description="预计送达时间")
    scheduled_time: Optional[str] = Field(None, description="预约上门时间")
    tracking_history: List[TrackingRecord] = Field([], description="物流轨迹")

class OrderSummary(BaseModel):
    """订单摘要"""
    order_id: str = Field(..., description="订单号")
    status: str = Field(..., description="状态代码")
    status_text: str = Field(..., description="状态文本")
    delivery_address: str = Field(..., description="配送地址")
    estimated_delivery: Optional[str] = Field(None, description="预计送达时间")

class ScheduleRequest(BaseModel):
    """预约请求"""
    scheduled_time: str = Field(..., description="预约时间 (格式: YYYY-MM-DD HH:MM:SS)")
    action: str = Field(..., description="操作类型: confirm(确认) 或 change(变更)")

class ScheduleResponse(BaseModel):
    """预约响应"""
    order_id: str = Field(..., description="订单号")
    scheduled_time: str = Field(..., description="预约时间")
    status: str = Field(..., description="订单状态")
    status_text: str = Field(..., description="状态文本")

# 状态映射
STATUS_MAP = {
    "pending": "待揽收",
    "picked_up": "已揽收",
    "in_transit": "运输中",
    "out_for_delivery": "派送中",
    "delivered": "已签收",
    "failed": "配送失败",
    "returned": "已退回"
}

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", tags=["系统"])
async def root():
    """API 根路径"""
    return {
        "service": "物流演示系统 API",
        "version": "1.0.0",
        "description": "为 YCloud AI 机器人提供物流查询和预约服务",
        "endpoints": {
            "查询订单": "GET /api/orders/{order_id}",
            "预约时间": "POST /api/orders/{order_id}/schedule",
            "按电话查询": "GET /api/orders/by-phone/{phone}"
        }
    }

@app.get("/api/orders/{order_id}", tags=["订单查询"])
async def get_order(
    order_id: str = Path(..., description="订单号", example="ORD20251102001")
):
    """
    查询订单物流状态
    
    根据订单号查询订单的详细信息和物流轨迹
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询订单
    cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "订单不存在",
                "order_id": order_id
            }
        )
    
    # 查询物流轨迹
    cursor.execute(
        "SELECT status, location, description, timestamp FROM tracking_history WHERE order_id = ? ORDER BY timestamp ASC",
        (order_id,)
    )
    tracking_records = cursor.fetchall()
    
    conn.close()
    
    # 构建响应
    tracking_history = [
        {
            "status": record["status"],
            "location": record["location"],
            "description": record["description"],
            "timestamp": record["timestamp"]
        }
        for record in tracking_records
    ]
    
    return {
        "success": True,
        "data": {
            "order_id": order["order_id"],
            "customer_name": order["customer_name"],
            "customer_phone": order["customer_phone"],
            "pickup_address": order["pickup_address"],
            "delivery_address": order["delivery_address"],
            "package_type": order["package_type"],
            "status": order["status"],
            "status_text": STATUS_MAP.get(order["status"], order["status"]),
            "current_location": order["current_location"],
            "estimated_delivery": order["estimated_delivery"],
            "scheduled_time": order["scheduled_time"],
            "tracking_history": tracking_history
        }
    }

@app.get("/api/orders/by-phone/{phone}", tags=["订单查询"])
async def get_orders_by_phone(
    phone: str = Path(..., description="客户电话号码", example="+8613800138000")
):
    """
    根据电话号码查询客户的所有订单
    
    返回该电话号码关联的所有订单摘要
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询订单
    cursor.execute(
        "SELECT order_id, status, delivery_address, estimated_delivery FROM orders WHERE customer_phone = ? ORDER BY created_at DESC",
        (phone,)
    )
    orders = cursor.fetchall()
    
    conn.close()
    
    if not orders:
        return {
            "success": True,
            "count": 0,
            "data": [],
            "message": "未找到该电话号码的订单"
        }
    
    # 构建响应
    order_list = [
        {
            "order_id": order["order_id"],
            "status": order["status"],
            "status_text": STATUS_MAP.get(order["status"], order["status"]),
            "delivery_address": order["delivery_address"],
            "estimated_delivery": order["estimated_delivery"]
        }
        for order in orders
    ]
    
    return {
        "success": True,
        "count": len(order_list),
        "data": order_list
    }

@app.post("/api/orders/{order_id}/schedule", tags=["预约管理"])
async def schedule_delivery(
    order_id: str = Path(..., description="订单号", example="ORD20251102001"),
    request: ScheduleRequest = Body(..., description="预约请求")
):
    """
    确认或变更上门配送时间
    
    允许客户预约或变更配送时间，仅支持状态为"派送中"的订单
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询订单
    cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "订单不存在",
                "order_id": order_id
            }
        )
    
    # 检查订单状态
    current_status = order["status"]
    if current_status not in ["in_transit", "out_for_delivery"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "该订单当前状态不支持预约",
                "current_status": current_status,
                "current_status_text": STATUS_MAP.get(current_status, current_status)
            }
        )
    
    # 验证时间格式
    try:
        datetime.strptime(request.scheduled_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式"
            }
        )
    
    # 更新预约时间
    cursor.execute(
        "UPDATE orders SET scheduled_time = ?, updated_at = ? WHERE order_id = ?",
        (request.scheduled_time, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), order_id)
    )
    
    # 如果订单还在运输中，更新为派送中
    if current_status == "in_transit":
        cursor.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?",
            ("out_for_delivery", order_id)
        )
        new_status = "out_for_delivery"
    else:
        new_status = current_status
    
    conn.commit()
    conn.close()
    
    # 确定消息
    if request.action == "confirm":
        message = "预约时间已确认"
    elif request.action == "change":
        message = "预约时间已变更"
    else:
        message = "预约时间已更新"
    
    return {
        "success": True,
        "message": message,
        "data": {
            "order_id": order_id,
            "scheduled_time": request.scheduled_time,
            "status": new_status,
            "status_text": STATUS_MAP.get(new_status, new_status)
        }
    }

@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders")
        count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_orders": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
