# 钱值时光机 技术需求文档（TRD）
项目名称：钱值时光机 (Wealth Time Machine)
版本：v1.0
状态：详细设计阶段

---

## 系统架构概述 (System Architecture)
系统采用前后端分离架构，核心逻辑由后端 API 驱动，AI 增强功能通过 RAG 架构实现。

- 前端：微信小程序原生框架 (WXML/WXSS/JS)
- 后端：Python FastAPI (高性能异步 Web 框架)
- 数据库：
  - 关系型数据库：PostgreSQL，存储宏观经济指数、城市物价、人均收入
  - 缓存：Redis，存储高频计算结果和静态索引
  - 向量库：ChromaDB/Qdrant，存储非结构化物价史料供 RAG 检索
- AI 接口：DeepSeek-V3 API，用于文案生成及数据清洗

---

## 数据库逻辑设计 (Database Schema)

### 宏观经济数据表 (macro_economics)
存储 1980 年至 2026 年的国家级统计数据。

| 字段名 | 类型 | 约束 | 说明 |
| ---- | ---- | ---- | ---- |
| year | INT | PK | 年份 (1980-2026) |
| cpi_index | DECIMAL | NOT NULL | 官方 CPI 累计指数 |
| m2_growth | DECIMAL | NOT NULL | M2 货币供应增速 |
| gdp_growth | DECIMAL | NOT NULL | GDP 增长率 |
| m2_adj | DECIMAL | NOT NULL | 计算得出的 M2 修正因子 (M2 - GDP) |

### 城市索引表 (city_data)
存储各级城市的基础能级及生活成本基准。

| 字段名 | 类型 | 说明 |
| ---- | ---- | ---- |
| city_id | INT | PK（全国城市行政区划代码） |
| city_name | VARCHAR | 城市名称（如：上海、开封） |
| coli_index | DECIMAL | 城市生活成本指数 (上海=100) |
| median_income | DECIMAL | 该城市最新年度人均可支配收入中位数 |
| region_level | INT | 1-省会/直辖市，2-地级市 |

---

## 核心算法实现规范 (Core Algorithms)

### 时空等值转换算法
实现 PRD 中的“三位一体”模型：
Value_now = Value_past × (0.4×CPI_now/CPI_past + 0.4×M2_adj_now/M2_adj_past + 0.2×Property_now/Property_past)

开发要求：
- 权重可调：后端需支持配置文件动态修改 0.4/0.4/0.2 的比例
- 数据平滑：若目标城市特定年份 Property 数据缺失，需回退至该省份平均房价

### 财富漂流等效购买力算法
Equivalent_Amount = Amount_source × COLI_source / COLI_target

### 身份判定逻辑
Ratio = Equivalent_Amount / Target_City_Median_Income
根据 Ratio 返回对应的 identity_tag（如：县城土豪、体面名流等）。

---

## API 接口定义 (API Specifications)

### 转换接口 POST /api/v1/convert

**Request Body**
```json
{
  "amount": 1000,
  "source_year": 1990,
  "city": "开封"
}
**Response Body**
{
  "equivalent_amount": 4280.00,
  "items": [
    {"name": "猪肉", "past": "200斤", "now": "30斤"},
    {"name": "房价", "past": "0.5平米", "now": "0.05平米"}
  ],
  "ai_comment": "在1990年的开封..."
}

