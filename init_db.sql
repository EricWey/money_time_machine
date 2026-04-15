-- 1. 宏观经济数据表：存储三位一体模型所需的核心指数
CREATE TABLE macro_economics (
    year INT PRIMARY KEY,                       -- 年份 (1980-2026)
    cpi_index DECIMAL(18, 4) NOT NULL,          -- 官方 CPI 累计指数 (以1980或特定年为基准)
    m2_growth DECIMAL(18, 4) NOT NULL,          -- M2 货币供应同比增速 (%)
    gdp_growth DECIMAL(18, 4) NOT NULL,          -- GDP 同比增速 (%)
    m2_adj DECIMAL(18, 4) NOT NULL,             -- M2 修正因子 (M2增速 - GDP增速)
    property_index_nat DECIMAL(18, 4),          -- 全国平均房价指数 (作为兜底)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 城市索引表：存储生活成本指数 (COLI) 和城市基础信息
CREATE TABLE city_data (
    city_id INT PRIMARY KEY,                    -- 行政区划代码
    city_name VARCHAR(50) NOT NULL,             -- 城市名称 (如：上海)
    province VARCHAR(50) NOT NULL,              -- 所属省份 (用于数据兜底逻辑)
    coli_index DECIMAL(18, 2) NOT NULL,         -- 生活成本指数 (上海=100)
    median_income DECIMAL(18, 2),               -- 该城市人均可支配收入中位数 (最新)
    region_level INT DEFAULT 2,                 -- 1: 一线/省会, 2: 地级市
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 历史物价与实物矩阵表：供转换器展示实物对比
CREATE TABLE city_prices (
    id SERIAL PRIMARY KEY,
    city_id INT REFERENCES city_data(city_id),
    year INT NOT NULL,
    category VARCHAR(20),                       -- 分类：food, housing, transport, service
    item_name VARCHAR(50),                      -- 实物名称：猪肉, 烩面, 房价
    price DECIMAL(18, 2),                       -- 单价
    unit VARCHAR(10),                           -- 单位：斤, 平米, 次
    is_essential BOOLEAN DEFAULT TRUE           -- 是否属于基础生存篮子
);

-- 索引优化
CREATE INDEX idx_city_year ON city_prices(city_id, year);
CREATE INDEX idx_macro_year ON macro_economics(year);