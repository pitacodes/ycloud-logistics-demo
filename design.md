# 物流演示系统设计文档

## 数据库设计

### 订单表 (orders)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| order_id | TEXT PRIMARY KEY | 订单号 (格式: ORD20250101001) |
| customer_name | TEXT | 客户姓名 |
| customer_phone | TEXT | 客户电话 |
| pickup_address | TEXT | 取件地址 |
| delivery_address | TEXT | 配送地址 |
| package_type | TEXT | 包裹类型 (文件/小件/大件/易碎品) |
| status | TEXT | 物流状态 |
| current_location | TEXT | 当前位置 |
| estimated_delivery | TEXT | 预计送达时间 |
| scheduled_time | TEXT | 预约上门时间 |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |

### 物流状态枚举

- `pending` - 待揽收
- `picked_up` - 已揽收
- `in_transit` - 运输中
- `out_for_delivery` - 派送中
- `delivered` - 已签收
- `failed` - 配送失败
- `returned` - 已退回

### 物流轨迹表 (tracking_history)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER PRIMARY KEY | 自增ID |
| order_id | TEXT | 订单号 (外键) |
| status | TEXT | 状态 |
| location | TEXT | 位置 |
| description | TEXT | 描述 |
| timestamp | TEXT | 时间戳 |

## API接口设计

### 1. 查询订单物流状态

**接口路径**: `GET /api/orders/{order_id}`

**请求参数**:
- `order_id` (路径参数): 订单号

**成功响应** (200):
```json
{
  "success": true,
  "data": {
    "order_id": "ORD20250103001",
    "customer_name": "张三",
    "customer_phone": "+8613800138000",
    "pickup_address": "北京市朝阳区建国路1号",
    "delivery_address": "上海市浦东新区陆家嘴环路1000号",
    "package_type": "小件",
    "status": "in_transit",
    "status_text": "运输中",
    "current_location": "上海分拨中心",
    "estimated_delivery": "2025-01-05 18:00:00",
    "scheduled_time": null,
    "tracking_history": [
      {
        "status": "picked_up",
        "location": "北京朝阳营业点",
        "description": "快递员已揽收",
        "timestamp": "2025-01-03 09:30:00"
      },
      {
        "status": "in_transit",
        "location": "北京分拨中心",
        "description": "到达分拨中心",
        "timestamp": "2025-01-03 14:20:00"
      },
      {
        "status": "in_transit",
        "location": "上海分拨中心",
        "description": "到达目的地分拨中心",
        "timestamp": "2025-01-04 08:15:00"
      }
    ]
  }
}
```

**失败响应** (404):
```json
{
  "success": false,
  "error": "订单不存在",
  "order_id": "ORD99999999"
}
```

### 2. 确认/变更上门时间

**接口路径**: `POST /api/orders/{order_id}/schedule`

**请求参数**:
- `order_id` (路径参数): 订单号
- 请求体 (JSON):
```json
{
  "scheduled_time": "2025-01-05 14:00:00",
  "action": "confirm"
}
```

**字段说明**:
- `scheduled_time`: 预约时间 (格式: YYYY-MM-DD HH:MM:SS)
- `action`: 操作类型 (`confirm` 确认 / `change` 变更)

**成功响应** (200):
```json
{
  "success": true,
  "message": "预约时间已确认",
  "data": {
    "order_id": "ORD20250103001",
    "scheduled_time": "2025-01-05 14:00:00",
    "status": "out_for_delivery",
    "status_text": "派送中"
  }
}
```

**失败响应** (400):
```json
{
  "success": false,
  "error": "该订单当前状态不支持预约",
  "current_status": "delivered"
}
```

### 3. 额外辅助接口 - 查询客户所有订单

**接口路径**: `GET /api/orders/by-phone/{phone}`

**请求参数**:
- `phone` (路径参数): 客户电话号码

**成功响应** (200):
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "order_id": "ORD20250103001",
      "status": "in_transit",
      "status_text": "运输中",
      "delivery_address": "上海市浦东新区陆家嘴环路1000号",
      "estimated_delivery": "2025-01-05 18:00:00"
    },
    {
      "order_id": "ORD20250102015",
      "status": "delivered",
      "status_text": "已签收",
      "delivery_address": "北京市海淀区中关村大街1号",
      "estimated_delivery": "2025-01-03 10:00:00"
    }
  ]
}
```

## YCloud 数据连接器配置建议

### 连接器1: 查询订单状态
- **名称**: 查询物流订单
- **方法**: GET
- **URL**: `http://localhost:8000/api/orders/{order_id}`
- **测试订单号**: ORD20250103001
- **返回变量映射**:
  - `status_text` → 物流状态
  - `current_location` → 当前位置
  - `estimated_delivery` → 预计送达时间
  - `tracking_history` → 物流轨迹

### 连接器2: 预约上门时间
- **名称**: 预约配送时间
- **方法**: POST
- **URL**: `http://localhost:8000/api/orders/{order_id}/schedule`
- **请求体**: 
  ```json
  {
    "scheduled_time": "{时间}",
    "action": "confirm"
  }
  ```
- **返回变量映射**:
  - `message` → 操作结果
  - `scheduled_time` → 预约时间

### 连接器3: 查询客户订单列表
- **名称**: 查询客户所有订单
- **方法**: GET
- **URL**: `http://localhost:8000/api/orders/by-phone/{phone}`
- **测试电话**: +8613800138000
- **返回变量映射**:
  - `count` → 订单数量
  - `data` → 订单列表

## 行动指南示例

```
当用户提供订单号并询问物流状态时:
1. 调用"查询物流订单"数据连接器
2. 将订单号作为参数传入
3. 向用户报告: 物流状态、当前位置、预计送达时间
4. 如果用户需要详细轨迹,展示tracking_history中的信息

当用户想要预约或变更配送时间时:
1. 首先确认订单号
2. 询问用户期望的配送时间
3. 调用"预约配送时间"数据连接器
4. 传入订单号和时间参数
5. 向用户确认预约结果

当用户只提供电话号码时:
1. 调用"查询客户所有订单"数据连接器
2. 展示该客户的所有订单
3. 询问用户想查询哪个订单的详细信息
```
