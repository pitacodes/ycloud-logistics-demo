#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物流演示系统 - 数据库初始化脚本
"""

import sqlite3
import random
from datetime import datetime, timedelta

# 数据库文件路径
DB_PATH = '/home/ubuntu/logistics_demo/logistics.db'

# 示例数据
CUSTOMER_NAMES = [
    "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
    "郑十一", "王芳", "刘洋", "陈静", "杨帆", "黄磊", "朱莉", "林峰",
    "何敏", "罗强", "梁婷", "宋伟", "唐丽", "许刚", "韩雪", "冯涛",
    "曹娜", "袁杰", "邓超", "彭飞", "苏敏", "卢强", "蒋丽", "蔡伟",
    "丁芳", "余涛", "杜娜", "叶刚", "程丽", "魏强", "薛芳", "雷涛"
]

PHONE_PREFIXES = ["138", "139", "186", "188", "159", "158", "157", "150"]

CITIES = [
    {"name": "北京", "districts": ["朝阳区", "海淀区", "东城区", "西城区", "丰台区"]},
    {"name": "上海", "districts": ["浦东新区", "黄浦区", "徐汇区", "静安区", "长宁区"]},
    {"name": "广州", "districts": ["天河区", "越秀区", "海珠区", "荔湾区", "白云区"]},
    {"name": "深圳", "districts": ["南山区", "福田区", "罗湖区", "宝安区", "龙岗区"]},
    {"name": "杭州", "districts": ["西湖区", "上城区", "下城区", "江干区", "拱墅区"]},
    {"name": "成都", "districts": ["武侯区", "锦江区", "青羊区", "金牛区", "成华区"]},
    {"name": "南京", "districts": ["鼓楼区", "玄武区", "秦淮区", "建邺区", "雨花台区"]},
    {"name": "武汉", "districts": ["武昌区", "汉口区", "汉阳区", "洪山区", "江汉区"]}
]

STREETS = ["建国路", "人民路", "中山路", "解放路", "和平路", "胜利路", "文化路", "光明路", "新华路", "中关村大街", "陆家嘴环路", "天河路"]

PACKAGE_TYPES = ["文件", "小件", "大件", "易碎品"]

STATUSES = [
    {"code": "pending", "text": "待揽收", "weight": 5},
    {"code": "picked_up", "text": "已揽收", "weight": 10},
    {"code": "in_transit", "text": "运输中", "weight": 30},
    {"code": "out_for_delivery", "text": "派送中", "weight": 25},
    {"code": "delivered", "text": "已签收", "weight": 25},
    {"code": "failed", "text": "配送失败", "weight": 3},
    {"code": "returned", "text": "已退回", "weight": 2}
]

def generate_phone():
    """生成随机电话号码"""
    prefix = random.choice(PHONE_PREFIXES)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"+86{prefix}{suffix}"

def generate_address(city_info):
    """生成随机地址"""
    district = random.choice(city_info["districts"])
    street = random.choice(STREETS)
    number = random.randint(1, 9999)
    return f"{city_info['name']}{district}{street}{number}号"

def generate_order_id(index):
    """生成订单号"""
    date_str = (datetime.now() - timedelta(days=random.randint(0, 10))).strftime("%Y%m%d")
    return f"ORD{date_str}{index:03d}"

def get_random_status():
    """根据权重随机选择状态"""
    weights = [s["weight"] for s in STATUSES]
    return random.choices(STATUSES, weights=weights)[0]

def generate_tracking_history(order_id, status_code, pickup_city, delivery_city, created_at):
    """生成物流轨迹"""
    history = []
    
    # 根据状态生成相应的轨迹
    if status_code == "pending":
        history.append({
            "order_id": order_id,
            "status": "pending",
            "location": f"{pickup_city}营业点",
            "description": "订单已创建，等待揽收",
            "timestamp": created_at
        })
    
    elif status_code in ["picked_up", "in_transit", "out_for_delivery", "delivered", "failed", "returned"]:
        # 已揽收
        ts = created_at + timedelta(hours=random.randint(1, 4))
        history.append({
            "order_id": order_id,
            "status": "picked_up",
            "location": f"{pickup_city}营业点",
            "description": "快递员已揽收",
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        if status_code in ["in_transit", "out_for_delivery", "delivered", "failed", "returned"]:
            # 到达始发分拨中心
            ts += timedelta(hours=random.randint(3, 6))
            history.append({
                "order_id": order_id,
                "status": "in_transit",
                "location": f"{pickup_city}分拨中心",
                "description": "到达分拨中心",
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # 运输中
            ts += timedelta(hours=random.randint(12, 24))
            history.append({
                "order_id": order_id,
                "status": "in_transit",
                "location": f"{delivery_city}分拨中心",
                "description": "到达目的地分拨中心",
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        if status_code in ["out_for_delivery", "delivered", "failed"]:
            # 派送中
            ts += timedelta(hours=random.randint(2, 4))
            history.append({
                "order_id": order_id,
                "status": "out_for_delivery",
                "location": f"{delivery_city}营业点",
                "description": "快递员正在派送",
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        if status_code == "delivered":
            # 已签收
            ts += timedelta(hours=random.randint(1, 3))
            history.append({
                "order_id": order_id,
                "status": "delivered",
                "location": f"{delivery_city}营业点",
                "description": "已签收，签收人: 本人",
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        elif status_code == "failed":
            # 配送失败
            ts += timedelta(hours=random.randint(1, 2))
            history.append({
                "order_id": order_id,
                "status": "failed",
                "location": f"{delivery_city}营业点",
                "description": "配送失败，客户不在家",
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        elif status_code == "returned":
            # 已退回
            ts += timedelta(hours=random.randint(1, 2))
            history.append({
                "order_id": order_id,
                "status": "failed",
                "location": f"{delivery_city}营业点",
                "description": "多次配送失败",
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            ts += timedelta(days=random.randint(1, 3))
            history.append({
                "order_id": order_id,
                "status": "returned",
                "location": f"{pickup_city}营业点",
                "description": "包裹已退回寄件地",
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
            })
    
    return history

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建订单表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        pickup_address TEXT NOT NULL,
        delivery_address TEXT NOT NULL,
        package_type TEXT NOT NULL,
        status TEXT NOT NULL,
        current_location TEXT,
        estimated_delivery TEXT,
        scheduled_time TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')
    
    # 创建物流轨迹表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tracking_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        status TEXT NOT NULL,
        location TEXT NOT NULL,
        description TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (order_id)
    )
    ''')
    
    conn.commit()
    return conn, cursor

def generate_demo_data(cursor, count=35):
    """生成演示数据"""
    print(f"开始生成 {count} 条演示订单数据...")
    
    for i in range(1, count + 1):
        # 基本信息
        order_id = generate_order_id(i)
        customer_name = random.choice(CUSTOMER_NAMES)
        customer_phone = generate_phone()
        
        # 地址信息
        pickup_city_info = random.choice(CITIES)
        delivery_city_info = random.choice([c for c in CITIES if c != pickup_city_info])
        
        pickup_address = generate_address(pickup_city_info)
        delivery_address = generate_address(delivery_city_info)
        
        # 包裹类型
        package_type = random.choice(PACKAGE_TYPES)
        
        # 状态
        status_info = get_random_status()
        status = status_info["code"]
        
        # 时间
        created_at = datetime.now() - timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))
        updated_at = created_at + timedelta(hours=random.randint(1, 48))
        
        # 当前位置
        if status == "pending":
            current_location = f"{pickup_city_info['name']}营业点"
        elif status == "picked_up":
            current_location = f"{pickup_city_info['name']}分拨中心"
        elif status == "in_transit":
            current_location = f"{delivery_city_info['name']}分拨中心"
        elif status in ["out_for_delivery", "failed"]:
            current_location = f"{delivery_city_info['name']}营业点"
        elif status == "delivered":
            current_location = f"{delivery_city_info['name']}营业点"
        else:  # returned
            current_location = f"{pickup_city_info['name']}营业点"
        
        # 预计送达时间
        if status in ["pending", "picked_up", "in_transit", "out_for_delivery"]:
            estimated_delivery = (datetime.now() + timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d %H:%M:%S")
        else:
            estimated_delivery = updated_at.strftime("%Y-%m-%d %H:%M:%S")
        
        # 预约时间 (部分订单有预约)
        scheduled_time = None
        if status == "out_for_delivery" and random.random() > 0.5:
            scheduled_time = (datetime.now() + timedelta(days=1, hours=random.randint(9, 18))).strftime("%Y-%m-%d %H:%M:%S")
        
        # 插入订单
        cursor.execute('''
        INSERT INTO orders (
            order_id, customer_name, customer_phone, pickup_address, delivery_address,
            package_type, status, current_location, estimated_delivery, scheduled_time,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id, customer_name, customer_phone, pickup_address, delivery_address,
            package_type, status, current_location, estimated_delivery, scheduled_time,
            created_at.strftime("%Y-%m-%d %H:%M:%S"), updated_at.strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        # 生成物流轨迹
        tracking_history = generate_tracking_history(
            order_id, status, pickup_city_info['name'], delivery_city_info['name'], created_at
        )
        
        for track in tracking_history:
            cursor.execute('''
            INSERT INTO tracking_history (order_id, status, location, description, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', (track["order_id"], track["status"], track["location"], track["description"], track["timestamp"]))
        
        print(f"  [{i}/{count}] 订单 {order_id} - {customer_name} - {status_info['text']}")
    
    print(f"\n成功生成 {count} 条订单数据!")

def main():
    """主函数"""
    print("=" * 60)
    print("物流演示系统 - 数据库初始化")
    print("=" * 60)
    
    conn, cursor = init_database()
    print("\n✓ 数据库表创建成功")
    
    generate_demo_data(cursor, count=35)
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ 数据库初始化完成: {DB_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()
