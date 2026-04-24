# 钱值时光机

钱值时光机是一个前后端分离的微信小程序项目，用来回答两个问题：

- 过去某一年的一笔钱，放到今天大概还有多少购买力
- 同样一份月收入，换到另一座城市生活，体感会发生什么变化

仓库同时包含 FastAPI 后端和微信小程序前端，支持本地开发联调、接口测试和页面迭代。

## 项目概览

项目由两部分组成：

- Python FastAPI 后端：提供购买力换算、财富漂流、宏观数据查询和 AI 文案生成接口
- 微信小程序前端：负责输入收集、接口调用、结果展示、海报生成与分享

当前开发配置以本地联调为默认方式：

- 小程序 `develop` 环境默认请求 `http://127.0.0.1:8000`
- 小程序 `trial` / `release` 环境必须切换到真实可访问的测试或生产 API 域名

## 主要功能

### 时空等值转换器

页面：`pages/time_machine/time_machine`

输入：

- 金额 `amount`
- 起始年份 `source_year`
- 城市 `city`

输出：

- `equivalent_amount`：折算到 2024 年的等值金额
- `items`：3 条商品价格对比
- `ai_comment`：AI 时代感点评

页面特性：

- 复古视觉风格
- 统一接口请求与错误处理
- 商品价格卡片展示

### 财富漂流瓶

页面：`pages/wealth_drift/wealth_drift`

输入：

- 当前城市 `current_city`
- 目标城市 `target_city`
- 月收入 `monthly_income`

输出：

- `equivalent_amount`：迁移后的等值购买力
- `wealth_ratio`：等值收入 / 目标城市中位收入
- `identity_label`：身份标签
- `city_comparison`：城市差异文案
- `ai_essay`：AI 感言

页面特性：

- 城市搜索与选择
- 漂流结果结构化展示
- AI 点评补充
- 海报生成、保存和分享

## 技术栈

### 后端

- FastAPI
- Pydantic / pydantic-settings
- Supabase Python SDK
- Requests
- DeepSeek Chat Completions API

### 前端

- 微信小程序原生 WXML / WXSS / JavaScript
- `wx.request`
- Canvas 海报生成

## 目录结构

```text
money_time_machine/
├── main.py                              # FastAPI 入口
├── services/
│   ├── ai_service.py                    # AI 文案服务
│   ├── calculator.py                    # 购买力计算逻辑
│   ├── item_metadata.py                 # 商品元数据
│   ├── time_machine/
│   │   ├── api.js                       # 时光机接口封装
│   │   └── shared.js                    # 时光机共享常量
│   └── wealth_drift/
│       ├── presenter.js                 # 财富漂流展示数据整理
│       └── real.js                      # 财富漂流真实接口请求
├── utils/
│   ├── api.js                           # 小程序统一请求层
│   ├── apiConfig.js                     # 小程序环境 API 地址配置
│   ├── cache.js                         # 接口缓存
│   └── poster.js                        # 海报生成
├── pages/
│   ├── time_machine/                    # 时空等值转换器页面
│   └── wealth_drift/                    # 财富漂流瓶页面
├── backend/init_db.sql                  # 数据库建表脚本
├── seed_macro_data.py                   # 宏观数据导入脚本
├── seed_city_data.py                    # 城市价格数据导入脚本
├── test_health.py                       # 健康检查测试
├── test_drift.py                        # 核心接口与计算测试
├── API_TEST_GUIDE.md                    # convert 接口测试指南
└── DRIFT_API_TEST_GUIDE.md              # drift 接口测试指南
```

## 环境要求

推荐环境：

- Python 3.10+
- 微信开发者工具
- 可访问的 Supabase 项目
- 可用的 DeepSeek API Key

依赖列表见 `requirements.txt`。

## 安装步骤

### 1. 创建虚拟环境并安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建或更新 `.env`：

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

变量说明：

- `SUPABASE_URL`：Supabase 项目地址
- `SUPABASE_SERVICE_ROLE_KEY`：Supabase 服务端密钥
- `DEEPSEEK_API_KEY`：DeepSeek 接口密钥

说明：

- 缺少 Supabase 配置时，后端仍可启动，但真实数据接口会返回不可用错误
- 缺少 DeepSeek Key 时，涉及 AI 文案生成的接口会返回 502

## 本地开发启动

### 启动后端

方式一：

```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

方式二：

```bash
bash run.sh
```

本地服务地址：

```text
http://127.0.0.1:8000
```

Swagger 文档地址：

```text
http://127.0.0.1:8000/docs
```

### 启动小程序

1. 用微信开发者工具打开项目根目录
2. 保持当前环境为 `develop`
3. 小程序会通过 `utils/apiConfig.js` 默认请求 `http://127.0.0.1:8000`
4. 可直接在本地调试页面样式、交互和接口联动

## 小程序 API 配置

`utils/apiConfig.js` 当前规则如下：

- `develop`：默认使用 `http://127.0.0.1:8000`
- `trial`：需要手动填写测试环境域名
- `release`：需要手动填写生产环境域名

行为说明：

- 开发环境允许本地地址，方便做页面和交互细节修改
- 体验版和正式版不允许继续指向本地地址
- `trial` / `release` 未配置地址或误配到本地地址时，小程序会直接报错阻止继续使用

## 后端接口

### `GET /`

返回欢迎信息和 `/docs` 文档入口。

### `GET /health`

返回：

- `status`
- `app_name`
- `app_version`
- `database_status`

说明：

- Supabase 正常时，`database_status` 通常为 `connected`
- Supabase 未初始化时，`database_status` 为 `disconnected`

### `GET /api/v1/macro`

用于查询宏观经济数据，支持参数：

- `year`
- `start_year`
- `end_year`
- `limit`
- `offset`
- `sort`
- `order`

### `POST /api/v1/convert`

请求示例：

```json
{
  "amount": 100,
  "source_year": 1990,
  "city": "北京"
}
```

响应字段：

- `equivalent_amount`
- `items`
- `ai_comment`

### `POST /api/v1/drift`

请求示例：

```json
{
  "current_city": "上海",
  "monthly_income": 10000,
  "target_city": "成都"
}
```

响应字段：

- `current_city`
- `target_city`
- `current_city_coli`
- `target_city_coli`
- `equivalent_amount`
- `target_city_median_income`
- `wealth_ratio`
- `identity_label`
- `city_comparison`
- `ai_essay`

## 业务规则

### 时空换算公式

```text
equivalent_value
= amount × (0.4 × CPI比率 + 0.4 × M2修正累计比率 + 0.2 × 房产指数比率)
```

### 财富漂流公式

```text
equivalent_amount = monthly_income × current_city_coli / target_city_coli
wealth_ratio = equivalent_amount / target_city_median_income
```

### 身份标签规则

- `wealth_ratio > 5`：县城土豪
- `wealth_ratio > 2`：体面名流
- `wealth_ratio > 0.8`：平替生活
- `wealth_ratio <= 0.8`：生存挑战

## 开发说明

### 前端

- 小程序统一请求入口在 `utils/api.js`
- 时光机页面只保留真实接口调用，不再保留本地 mock 模式
- 财富漂流页面通过 `services/wealth_drift/real.js` 请求后端，并通过 `services/wealth_drift/presenter.js` 生成展示数据

### 后端

- 入口文件：`main.py`
- 购买力计算：`services/calculator.py`
- AI 调用：`services/ai_service.py`
- 数据导入脚本：`seed_macro_data.py`、`seed_city_data.py`

## 测试与验证

### 自动化测试

```bash
./venv/bin/pytest -q test_health.py test_drift.py
```

测试覆盖：

- 健康检查接口
- 货币购买力转换接口
- 财富漂流接口
- 核心计算函数

说明：

- 测试中对 Supabase 和 AI 请求做了 mock
- 适合本地快速回归验证，不依赖线上服务状态

### Python 语法检查

```bash
./venv/bin/python -m py_compile main.py services/ai_service.py services/calculator.py test_health.py test_drift.py
```

### 手工联调建议

1. 启动本地 FastAPI 服务
2. 用微信开发者工具打开项目并保持 `develop` 环境
3. 逐页验证输入、加载、错误提示、结果展示和海报功能
4. 需要看接口结构时，可访问本地 `/docs`

## 数据与部署说明

### 数据依赖

后端依赖 Supabase 中的真实数据表：

- `macro_economics`
- `city_data`
- `city_prices`

建表脚本见 `backend/init_db.sql`。

### 发布前检查

提交体验版或正式版前，建议至少确认：

- `utils/apiConfig.js` 中 `trial` / `release` 已配置正确域名
- 微信后台已配置 request 合法域名
- Supabase 数据完整
- DeepSeek API 可用
- 本地自动化测试通过
- 小程序关键页面手工联调通过

## 注意事项

- 当前默认开发联调地址就是 `http://127.0.0.1:8000`
- 如果本地后端未启动，小程序会直接提示网络错误
- Supabase 不可用时，`/api/v1/macro`、`/api/v1/convert`、`/api/v1/drift` 无法返回真实业务结果
- DeepSeek 不可用时，AI 文案接口会失败，不再自动生成本地兜底文案
- `wealth_drift` 页面展示模型仍依赖前端内置城市样本信息做展示排版
- `seed_macro_data.py` 里的 `is_forecast` 字段与当前建表脚本仍有差异，后续若继续完善数据导入需要一起调整

## 相关文档

- `API_TEST_GUIDE.md`
- `DRIFT_API_TEST_GUIDE.md`
- `backend/init_db.sql`
