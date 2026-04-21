# 钱值时光机

钱值时光机是一个前后端分离的小项目，核心目标是把“过去的一笔钱今天值多少”和“同样工资换个城市能过什么生活”做成可视化、可分享的体验。

当前仓库包含两部分：

- Python FastAPI 后端，负责购买力换算、城市漂流计算和 AI 文案生成
- 微信小程序前端，负责收集输入、调用接口并展示结果

## 1. 项目目标

项目围绕两个核心场景展开：

- 时空等值转换器：输入历史金额、年份、城市，计算在 2024 年的大致等值购买力
- 财富漂流瓶：输入当前城市、月收入、目标城市，估算迁移后的生活水平与身份标签

项目同时尝试引入 AI 文案，让结果更有情绪和传播性。

## 2. 当前仓库结构

```text
money_time_machine/
├── main.py                         # FastAPI 入口与接口定义
├── services/
│   ├── ai_service.py               # AI 文案服务
│   ├── calculator.py               # 购买力计算服务
│   └── fallback_data.py            # 无外部依赖时的本地兜底数据
├── pages/
│   ├── time_machine/               # 小程序：时空换算页
│   └── wealth_drift/               # 小程序：财富漂流页
├── init_db.sql                     # 数据库建表脚本
├── seed_macro_data.py              # 宏观数据初始化脚本
├── seed_city_data.py               # 城市数据初始化脚本
├── test_health.py                  # 健康检查测试
├── test_drift.py                   # 业务测试
├── PRD.md                          # 产品需求文档
├── TRD.md                          # 技术需求文档
├── API_TEST_GUIDE.md               # convert 接口测试说明
└── DRIFT_API_TEST_GUIDE.md         # drift 接口测试说明
```

## 3. 功能说明

### 3.1 时空等值转换器

输入：

- `amount`：原始金额，必须大于 0
- `source_year`：起始年份，当前限制为 1980-2025
- `city`：城市名称，当前内置校验城市为北京、上海、广州、深圳、杭州、成都、武汉、西安、南京、重庆

输出：

- `equivalent_amount`：折算后的等值金额
- `items`：商品价格对比列表
- `ai_comment`：AI 或兜底文案

计算公式：

```text
equivalent_value
= amount × (0.4 × CPI比率 + 0.4 × M2修正累计比率 + 0.2 × 房产指数比率)
```

### 3.2 财富漂流瓶

输入：

- `current_city`：当前城市
- `monthly_income`：月收入，必须大于 0
- `target_city`：目标城市

输出：

- `equivalent_amount`：换城后的等值购买力
- `wealth_ratio`：等值收入 / 目标城市中位数收入
- `identity_label`：身份标签
- `city_comparison`：城市差异描述
- `ai_essay`：AI 或兜底感言

计算公式：

```text
equivalent_amount = monthly_income × current_city_coli / target_city_coli
wealth_ratio = equivalent_amount / target_city_median_income
```

身份标签规则：

- `> 5`：县城土豪
- `> 2`：体面名流
- `> 0.8`：平替生活
- `<= 0.8`：生存挑战

## 4. 技术架构

### 后端

- 框架：FastAPI
- 配置：Pydantic Settings
- 数据源：Supabase
- AI：DeepSeek Chat Completions API

### 前端

- 框架：微信小程序原生 WXML / WXSS / JS
- 页面：
  - `pages/time_machine/time_machine`
  - `pages/wealth_drift/wealth_drift`

## 5. 数据设计

数据库核心表有三张：

- `macro_economics`
  - 按年份保存 CPI、M2、GDP、房价指数
- `city_data`
  - 保存城市 COLI、收入中位数、省份等基础信息
- `city_prices`
  - 保存城市-年份-商品维度的价格数据

注意：

- `init_db.sql` 里的 `city_prices` 通过 `city_id` 关联城市
- 原始代码按 `city_name` 直接查 `city_prices`，这一点已在代码中兼容处理

## 6. 运行说明

### 6.1 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6.2 环境变量

如果接 Supabase / DeepSeek，请配置 `.env`：

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 6.3 启动后端

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

或者：

```bash
bash run.sh
```

### 6.4 启动小程序

用微信开发者工具打开项目根目录即可。前端当前默认请求：

```text
http://127.0.0.1:8000
```

## 7. 兜底机制

为了让项目在本地没有 Supabase、没有 DeepSeek、甚至只是看代码时也能基本运行，我补了兜底策略：

- Supabase 未安装或环境变量缺失时，后端自动切换到本地样例数据
- DeepSeek Key 缺失时，AI 文案自动回退到模板文案
- `city_prices` 缺失时，接口回退到默认商品价格

这样至少可以保证：

- `/health` 可返回健康状态
- `/api/v1/convert` 在常见示例上可返回结果
- `/api/v1/drift` 在内置城市样例上可返回结果

## 8. 这次代码审阅发现的问题

### 已修复

- `main.py` 使用了未定义的 `logger`，会在城市查询失败时抛出运行错误
- 应用在导入阶段就强依赖 Supabase，缺配置时服务无法启动
- `/api/v1/convert` 会把 `HTTPException` 再包一层，导致错误语义不清
- `services/calculator.py` 查询 `city_prices` 时使用了和建表脚本不一致的 `city_name` 字段
- M2 累乘没有显式按年份排序，理论上会引入不稳定结果
- 商品购买力对比在 `price_then == 0` 时存在除零风险
- 小程序前端请求端口写成了 `8003`，与 `run.sh` 的 `8000` 不一致
- WXML 使用了 `h1` / `h2` 标签，不符合小程序语法习惯
- 小程序错误展示对 FastAPI 的数组型校验错误支持不足
- `app.json` 引用了 `sitemap.json`，但仓库里缺少该文件
- `requirements.txt` 缺少 `requests`，而 AI 服务实际依赖它

### 仍然存在的风险

- 本地环境当前未安装 `fastapi` / `pytest`，所以我无法在这个工作区直接跑接口与测试
- `test_drift.py` 与真实外部依赖强相关，后续更适合补 mock 或测试专用 fixture
- `seed_macro_data.py` 中使用了 `is_forecast` 字段，但 `init_db.sql` 目前没有该列
- `TRD.md` 里的 API 示例代码块存在未闭合片段，文档可读性一般
- 小程序当前城市输入仍是自由文本，长期看更适合改成下拉选择或可搜索选择器

## 9. 接口摘要

### `GET /health`

返回服务名、版本号和数据库状态。

### `GET /`

返回欢迎信息和文档入口。

### `POST /api/v1/convert`

示例：

```json
{
  "amount": 100,
  "source_year": 1990,
  "city": "北京"
}
```

### `POST /api/v1/drift`

示例：

```json
{
  "current_city": "上海",
  "monthly_income": 10000,
  "target_city": "开封"
}
```

## 10. 建议的下一步

- 补一套真正可运行的 `pytest` fixture，把 Supabase 和 AI 请求都 mock 掉
- 给小程序加城市选择器，避免用户输入非法城市
- 把后端的数据访问从 `main.py` 中拆出去，形成 repository/service 分层
- 补 README 中的接口响应示例截图和开发流程
