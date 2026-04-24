# 财富漂流瓶API测试指南

## API概述

**接口名称**：财富漂流瓶接口
**接口路径**：`/api/v1/drift`
**请求方法**：POST
**功能描述**：根据城市生活成本指数和收入水平，计算用户在不同城市间的财富购买力变化，并生成身份标签和AI感言

## 请求参数

### 请求头设置
```
Content-Type: application/json
```

### 请求体参数
| 参数名 | 类型 | 必填 | 验证规则 | 描述 |
|-------|------|------|---------|------|
| current_city | string | 是 | 1-50字符 | 当前所在城市 |
| monthly_income | float | 是 | 必须 > 0 | 月收入金额 |
| target_city | string | 是 | 1-50字符 | 目标迁移城市 |

### 支持的城市列表
上海、北京、深圳、郑州、开封、鹤岗

## 请求示例

### 1. 使用curl命令测试

```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/drift \
  -H "Content-Type: application/json" \
  -d '{
    "current_city": "上海",
    "monthly_income": 10000,
    "target_city": "开封"
  }'
```

### 2. 使用Postman测试

#### 步骤1：创建新请求
1. 打开Postman
2. 点击"New"创建新请求
3. 选择"POST"方法
4. 输入URL：`<YOUR_API_BASE_URL>/api/v1/drift`

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
  "current_city": "上海",
  "monthly_income": 10000,
  "target_city": "开封"
}
```

#### 步骤4：发送请求
1. 点击"Send"按钮
2. 查看响应结果

## 响应格式

### 成功响应示例
```json
{
  "current_city": "上海",
  "target_city": "开封",
  "current_city_coli": 100.0,
  "target_city_coli": 52.0,
  "equivalent_amount": 19230.77,
  "target_city_median_income": 2800.0,
  "wealth_ratio": 6.87,
  "identity_label": "县城土豪",
  "city_comparison": "上海地铁月卡的价格，够在开封打车满城跑一个月",
  "ai_essay": "沪上万元如流水，汴梁薪厚似归乡。数字背后是生活重量的迁徙——从精致生存到从容生活，这购买力跃升的密码，藏在早市烟火与不再焦虑的晚霞里。"
}
```

### 响应字段说明
| 字段名 | 类型 | 描述 |
|-------|------|------|
| current_city | string | 当前城市 |
| target_city | string | 目标城市 |
| current_city_coli | float | 当前城市COLI指数 |
| target_city_coli | float | 目标城市COLI指数 |
| equivalent_amount | float | 等值收入金额 |
| target_city_median_income | float | 目标城市中位数收入 |
| wealth_ratio | float | 财富比率 |
| identity_label | string | 身份标签 |
| city_comparison | string | 城市对比描述 |
| ai_essay | string | AI生成的感言 |

## 身份标签说明

| 财富比率范围 | 身份标签 | 说明 |
|------------|---------|------|
| Ratio > 5 | 县城土豪 | 购买力远超当地平均水平 |
| 2 < Ratio <= 5 | 体面名流 | 购买力高于当地平均水平 |
| 0.8 < Ratio <= 2 | 平替生活 | 购买力与当地平均水平相当 |
| Ratio <= 0.8 | 生存挑战 | 购买力低于当地平均水平 |

## 业务逻辑说明

### 等值收入计算公式
```
equivalent_amount = monthly_income * (current_city_coli / target_city_coli)
```

### 财富比率计算公式
```
Wealth_Ratio = equivalent_amount / target_city_median_income
```

### 示例计算
以"上海月薪10000元，迁移到开封"为例：
- 上海COLI指数 = 100
- 开封COLI指数 = 52
- 等值收入 = 10000 * (100 / 52) = 19230.77元
- 开封中位数收入 = 2800元
- 财富比率 = 19230.77 / 2800 = 6.87
- 身份标签 = "县城土豪"（Ratio > 5）

## 测试用例

### 测试用例1：上海高薪迁移到开封（县城土豪）
```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/drift \
  -H "Content-Type: application/json" \
  -d '{
    "current_city": "上海",
    "monthly_income": 10000,
    "target_city": "开封"
  }'
```

**预期结果**：
- identity_label: "县城土豪"
- wealth_ratio: > 5
- 等值收入 > 目标城市中位数收入的5倍

### 测试用例2：北京高薪迁移到鹤岗（县城土豪）
```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/drift \
  -H "Content-Type: application/json" \
  -d '{
    "current_city": "北京",
    "monthly_income": 8000,
    "target_city": "鹤岗"
  }'
```

**预期结果**：
- identity_label: "县城土豪"
- wealth_ratio: > 5
- 等值收入 > 目标城市中位数收入的5倍

### 测试用例3：上海中等收入迁移到郑州（体面名流）
```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/drift \
  -H "Content-Type: application/json" \
  -d '{
    "current_city": "上海",
    "monthly_income": 5000,
    "target_city": "郑州"
  }'
```

**预期结果**：
- identity_label: "体面名流"
- wealth_ratio: 2 < ratio <= 5

### 测试用例4：相同城市错误
```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/drift \
  -H "Content-Type: application/json" \
  -d '{
    "current_city": "上海",
    "monthly_income": 10000,
    "target_city": "上海"
  }'
```

**预期结果**：
- HTTP状态码: 422
- 错误信息: 包含"当前城市和目标城市不能相同"

### 测试用例5：城市数据不存在错误
```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/drift \
  -H "Content-Type: application/json" \
  -d '{
    "current_city": "长沙",
    "monthly_income": 10000,
    "target_city": "开封"
  }'
```

**预期结果**：
- HTTP状态码: 404
- 错误信息: "城市 长沙 数据不存在"

### 测试用例6：月收入为负数错误
```bash
curl -X POST <YOUR_API_BASE_URL>/api/v1/drift \
  -H "Content-Type: application/json" \
  -d '{
    "current_city": "上海",
    "monthly_income": -5000,
    "target_city": "开封"
  }'
```

**预期结果**：
- HTTP状态码: 422
- 错误信息: "Input should be greater than 0"

## 城市对比描述示例

根据不同COLI指数比值，生成不同类型的对比描述：

### 高比值场景（ratio > 1.5）
- "你在上海租一室户的钱，在开封能住带院子的二层楼"
- "北京的一碗面，够在鹤岗吃三顿"
- "深圳地铁月卡的价格，够在郑州打车满城跑一个月"

### 中等比值场景（1 < ratio <= 1.5）
- "你在北京月薪过万，扣除房租所剩无几；在鹤岗同样收入能过得体面"
- "上海的夜生活需要精打细算，郑州则可以随心所欲"
- "同样的工资，在北京是月光族，在开封是小康水平"

### 低比值场景（0.5 < ratio <= 1）
- "虽然郑州收入略低，但生活质量反而更高"
- "在北京舍不得打的，在上海可以随时叫车"
- "北京的水电费，够在郑州交双份还有余"

### 极低比值场景（ratio <= 0.5）
- "无论在北京还是上海，都得精打细算过日子"
- "两座城市的生活成本差距不大，关键看个人理财能力"
- "物价差不多，但深圳或许有更好的发展机会"

## 错误处理

| HTTP状态码 | 错误类型 | 描述 | 解决方法 |
|-----------|---------|------|---------|
| 400 | Bad Request | 请求参数错误 | 检查请求参数是否符合验证规则 |
| 404 | Not Found | 城市数据不存在 | 检查城市名称是否正确 |
| 422 | Validation Error | 参数验证失败 | 检查参数类型和范围 |
| 500 | Internal Server Error | 服务器内部错误 | 检查服务器日志，联系管理员 |

## 注意事项

1. **数据准确性**：城市生活成本指数基于公开数据和统计公报，仅供参考
2. **AI感言**：AI感言基于模型生成，可能存在主观性和创意性
3. **城市覆盖**：目前仅支持预置的6个城市
4. **性能考虑**：大量并发请求可能影响响应速度，建议合理控制请求频率

## 验证步骤

1. **确认服务地址**：确保真实测试环境或生产环境 API 域名可访问
2. **健康检查**：访问 `/health` 接口确认服务状态
3. **数据验证**：确保城市数据已通过 `seed_city_data.py` 脚本注入
4. **接口测试**：使用上述测试用例验证接口功能
5. **数据验证**：检查返回数据的准确性和完整性
6. **错误处理**：测试各种错误场景的处理能力

## 联系支持

如遇到问题，请提供以下信息：
- 请求URL和参数
- 错误响应内容
- 服务器日志
- 复现步骤
