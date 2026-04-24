# 货币购买力转换API测试指南

## API概述

**接口名称**：货币购买力转换接口  
**接口路径**：`/api/v1/convert`  
**请求方法**：POST  
**功能描述**：根据宏观经济数据计算不同年份货币的购买力变化，并提供实物价格对比和AI评价

## 请求参数

### 请求头设置
```
Content-Type: application/json
```

### 请求体参数
| 参数名 | 类型 | 必填 | 验证规则 | 描述 |
|-------|------|------|---------|------|
| amount | float | 是 | 必须 > 0 | 转换金额 |
| source_year | int | 是 | 1980-2025 | 起始年份 |
| city | string | 是 | 支持指定城市列表 | 城市名称 |

### 支持的城市列表
北京、上海、广州、深圳、杭州、成都、武汉、西安、南京、重庆

## 请求示例

### 1. 使用curl命令测试

```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/convert \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100,
    "source_year": 1990,
    "city": "北京"
  }'
```

### 2. 使用Postman测试

#### 步骤1：创建新请求
1. 打开Postman
2. 点击"New"创建新请求
3. 选择"POST"方法
4. 输入URL：`<YOUR_API_BASE_URL>/api/v1/convert`

#### 步骤2：设置请求头
1. 点击"Headers"标签
2. 添加新的header：
   - Key: `Content-Type`
   - Value: `application/json`

#### 步骤3：设置请求体
1. 点击"Body"标签
2. 选择"raw"格式
3. 选择"JSON"类型
4. 输入以下JSON数据：
```json
{
  "amount": 100,
  "source_year": 1990,
  "city": "北京"
}
```

#### 步骤4：发送请求
1. 点击"Send"按钮
2. 查看响应结果

### 3. 使用Python requests测试

```python
import requests
import json

url = "<YOUR_API_BASE_URL>/api/v1/convert"
headers = {
    "Content-Type": "application/json"
}
data = {
    "amount": 100,
    "source_year": 1990,
    "city": "北京"
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())
```

## 响应格式

### 成功响应示例
```json
{
  "equivalent_amount": 644.92,
  "items": [
    {
      "name": "猪肉",
      "price_then": 2.5,
      "price_now": 25.0,
      "purchasing_power": "上涨 900.0%"
    },
    {
      "name": "大米",
      "price_then": 0.8,
      "price_now": 6.0,
      "purchasing_power": "上涨 650.0%"
    },
    {
      "name": "鸡蛋",
      "price_then": 1.2,
      "price_now": 12.0,
      "purchasing_power": "上涨 900.0%"
    }
  ],
  "ai_comment": "1990年的100元，现在只值644.92元。那时候的物价，真是让人怀念啊！"
}
```

### 响应字段说明
| 字段名 | 类型 | 描述 |
|-------|------|------|
| equivalent_amount | float | 等价值（保留2位小数） |
| items | array | 商品对比列表 |
| items[].name | string | 商品名称 |
| items[].price_then | float | 起始年份价格 |
| items[].price_now | float | 当前年份价格 |
| items[].purchasing_power | string | 购买力变化描述 |
| ai_comment | string | AI评价 |

## 测试用例

### 测试用例1：正常转换请求
```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/convert \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100,
    "source_year": 1990,
    "city": "北京"
  }'
```

**预期结果**：返回成功的转换结果，包含等价值、商品对比和AI评价

### 测试用例2：不同年份转换
```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/convert \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "source_year": 2000,
    "city": "上海"
  }'
```

**预期结果**：返回2000年500元到2024年的等价值

### 测试用例3：不同城市转换
```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/convert \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "source_year": 2010,
    "city": "深圳"
  }'
```

**预期结果**：返回深圳地区的转换结果

## 错误处理

### 错误码说明

| HTTP状态码 | 错误类型 | 描述 | 解决方法 |
|-----------|---------|------|---------|
| 400 | Bad Request | 请求参数错误 | 检查请求参数是否符合验证规则 |
| 404 | Not Found | 接口不存在 | 检查请求URL是否正确 |
| 500 | Internal Server Error | 服务器内部错误 | 检查服务器日志，联系管理员 |

### 常见错误示例

#### 1. 参数验证错误
**请求示例**：
```json
{
  "amount": -100,
  "source_year": 1990,
  "city": "北京"
}
```

**错误响应**：
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

**解决方法**：确保amount大于0

#### 2. 城市名称错误
**请求示例**：
```json
{
  "amount": 100,
  "source_year": 1990,
  "city": "长沙"
}
```

**错误响应**：
```json
{
  "detail": "城市名称无效，支持的城市: 北京, 上海, 广州, 深圳, 杭州, 成都, 武汉, 西安, 南京, 重庆"
}
```

**解决方法**：使用支持的城市名称

#### 3. 年份超出范围
**请求示例**：
```json
{
  "amount": 100,
  "source_year": 1970,
  "city": "北京"
}
```

**错误响应**：
```json
{
  "detail": [
    {
      "loc": ["body", "source_year"],
      "msg": "ensure this value is greater than or equal to 1980",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**解决方法**：确保年份在1980-2025范围内

## 性能测试

### 压力测试示例
```bash
# 使用Apache Bench进行压力测试
ab -n 1000 -c 10 -H "Content-Type: application/json" \
   -p request.json \
   <YOUR_API_BASE_URL>/api/v1/convert
```

### request.json文件内容
```json
{
  "amount": 100,
  "source_year": 1990,
  "city": "北京"
}
```

## 注意事项

1. **数据准确性**：宏观经济数据基于历史统计，仅供参考
2. **AI评价**：AI评价基于模型生成，可能存在主观性
3. **价格数据**：实物价格数据需要在真实数据源中完整可用，否则接口会直接返回错误
4. **性能考虑**：大量并发请求可能影响响应速度
5. **API限制**：建议合理控制请求频率，避免过度调用

## 验证步骤

1. **启动服务**：确保FastAPI服务正常运行
2. **健康检查**：访问 `/health` 接口确认服务状态
3. **接口测试**：使用上述测试用例验证接口功能
4. **数据验证**：检查返回数据的准确性和完整性
5. **错误处理**：测试各种错误场景的处理能力

## 联系支持

如遇到问题，请提供以下信息：
- 请求URL和参数
- 错误响应内容
- 服务器日志
- 复现步骤
