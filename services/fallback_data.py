#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""无外部依赖时使用的本地兜底数据。"""

from __future__ import annotations

from typing import Dict, List

VALID_CITIES = [
    "北京",
    "上海",
    "天津",
    "重庆",
    "石家庄",
    "太原",
    "呼和浩特",
    "沈阳",
    "长春",
    "哈尔滨",
    "南京",
    "杭州",
    "合肥",
    "福州",
    "南昌",
    "济南",
    "郑州",
    "武汉",
    "长沙",
    "广州",
    "南宁",
    "海口",
    "成都",
    "贵阳",
    "昆明",
    "拉萨",
    "西安",
    "兰州",
    "西宁",
    "银川",
    "乌鲁木齐"
]

_RAW_CITY_DATA = [
    ("北京", 98.0, 7800.0, "北京市"),
    ("上海", 100.0, 8100.0, "上海市"),
    ("天津", 79.0, 5600.0, "天津市"),
    ("重庆", 72.0, 4600.0, "重庆市"),
    ("石家庄", 63.0, 4200.0, "河北省"),
    ("太原", 64.0, 4300.0, "山西省"),
    ("呼和浩特", 62.0, 4100.0, "内蒙古自治区"),
    ("沈阳", 68.0, 4700.0, "辽宁省"),
    ("长春", 63.0, 4200.0, "吉林省"),
    ("哈尔滨", 65.0, 4300.0, "黑龙江省"),
    ("南京", 84.0, 6500.0, "江苏省"),
    ("杭州", 88.0, 7100.0, "浙江省"),
    ("合肥", 66.0, 4600.0, "安徽省"),
    ("福州", 69.0, 4700.0, "福建省"),
    ("南昌", 64.0, 4300.0, "江西省"),
    ("济南", 67.0, 4600.0, "山东省"),
    ("郑州", 65.0, 4400.0, "河南省"),
    ("武汉", 74.0, 5000.0, "湖北省"),
    ("长沙", 69.0, 4700.0, "湖南省"),
    ("广州", 92.0, 7300.0, "广东省"),
    ("南宁", 60.0, 4000.0, "广西壮族自治区"),
    ("海口", 66.0, 4200.0, "海南省"),
    ("成都", 72.0, 4900.0, "四川省"),
    ("贵阳", 58.0, 3900.0, "贵州省"),
    ("昆明", 61.0, 4100.0, "云南省"),
    ("拉萨", 67.0, 4400.0, "西藏自治区"),
    ("西安", 70.0, 4600.0, "陕西省"),
    ("兰州", 60.0, 4000.0, "甘肃省"),
    ("西宁", 59.0, 3900.0, "青海省"),
    ("银川", 58.0, 3900.0, "宁夏回族自治区"),
    ("乌鲁木齐", 65.0, 4300.0, "新疆维吾尔自治区"),
]

_RAW_MACRO_DATA = [
    (1980, 6.0, 19.0, 7.9, 100),
    (1981, 2.4, 14.5, 5.1, 105),
    (1982, 1.9, 13.0, 9.0, 110),
    (1983, 1.5, 12.0, 10.8, 112),
    (1984, 2.8, 20.0, 15.2, 115),
    (1985, 9.3, 24.5, 13.5, 120),
    (1986, 6.5, 29.0, 8.9, 125),
    (1987, 7.3, 24.0, 11.7, 130),
    (1988, 18.8, 21.0, 11.3, 133),
    (1989, 18.0, 15.0, 4.2, 135),
    (1990, 3.1, 20.2, 3.9, 140),
    (1991, 3.4, 26.5, 9.3, 150),
    (1992, 6.4, 31.3, 14.2, 160),
    (1993, 14.7, 37.3, 13.9, 170),
    (1994, 24.1, 34.5, 13.0, 180),
    (1995, 17.1, 29.5, 10.9, 185),
    (1996, 8.3, 25.3, 9.9, 190),
    (1997, 2.8, 19.6, 9.2, 195),
    (1998, -0.8, 15.3, 7.8, 200),
    (1999, -1.4, 14.7, 7.7, 210),
    (2000, 0.4, 12.3, 8.5, 220),
    (2001, 0.7, 14.4, 8.3, 240),
    (2002, -0.8, 16.8, 9.1, 260),
    (2003, 1.2, 19.6, 10.0, 280),
    (2004, 3.9, 14.6, 10.1, 300),
    (2005, 1.8, 17.6, 11.4, 320),
    (2006, 1.5, 16.9, 12.7, 350),
    (2007, 4.8, 16.7, 14.2, 380),
    (2008, 5.9, 17.8, 9.6, 420),
    (2009, -0.7, 27.7, 9.4, 450),
    (2010, 3.3, 19.7, 10.6, 500),
    (2011, 5.4, 13.6, 9.6, 550),
    (2012, 2.6, 13.8, 7.9, 600),
    (2013, 2.6, 13.6, 7.8, 630),
    (2014, 2.0, 12.2, 7.4, 650),
    (2015, 1.4, 13.3, 7.0, 700),
    (2016, 2.0, 11.3, 6.8, 780),
    (2017, 1.6, 8.1, 6.9, 850),
    (2018, 2.1, 8.1, 6.7, 900),
    (2019, 2.9, 8.7, 6.0, 950),
    (2020, 2.5, 10.1, 2.2, 1000),
    (2021, 0.9, 9.0, 8.4, 1050),
    (2022, 2.0, 11.8, 3.0, 1020),
    (2023, 0.2, 9.7, 5.2, 1000),
    (2024, 0.2, 8.7, 5.0, 990),
    (2025, 0.8, 8.0, 5.0, 980),
]


def build_macro_fallback_data() -> Dict[int, dict]:
    current_cpi = 100.0
    data: Dict[int, dict] = {}
    for year, cpi_rate, m2_growth, gdp_growth, property_index in _RAW_MACRO_DATA:
        if year > 1980:
            current_cpi *= 1 + cpi_rate / 100
        data[year] = {
            "year": year,
            "cpi_index": round(current_cpi, 4),
            "m2_growth": m2_growth,
            "gdp_growth": gdp_growth,
            "m2_adj": round(m2_growth - gdp_growth, 4),
            "property_index_nat": property_index,
        }
    return data


FALLBACK_MACRO_DATA = build_macro_fallback_data()

FALLBACK_CITY_DATA = {
    city_name: {
        "city_name": city_name,
        "coli_index": coli_index,
        "median_income": median_income,
        "province": province,
    }
    for city_name, coli_index, median_income, province in _RAW_CITY_DATA
}

FALLBACK_CITY_PRICES: Dict[str, Dict[int, List[dict]]] = {
    "北京": {
        1990: [
            {"item_name": "梗米", "price": 0.8, "unit": "元/斤", "category": "food"},
            {"item_name": "大豆油", "price": 2.6, "unit": "元/升", "category": "food"},
            {"item_name": "精瘦肉", "price": 2.5, "unit": "元/斤", "category": "food"},
            {"item_name": "棉质T恤", "price": 18.0, "unit": "元/件", "category": "clothing"},
            {"item_name": "330ml啤酒", "price": 1.5, "unit": "元/瓶", "category": "beverage"},
            {"item_name": "500ml五粮液", "price": 98.0, "unit": "元/瓶", "category": "beverage"},
            {"item_name": "月平均工资", "price": 214.0, "unit": "元/月", "category": "income"},
            {"item_name": "理发", "price": 1.0, "unit": "元/次", "category": "service"},
        ],
        2024: [
            {"item_name": "梗米", "price": 6.2, "unit": "元/斤", "category": "food"},
            {"item_name": "大豆油", "price": 16.8, "unit": "元/升", "category": "food"},
            {"item_name": "精瘦肉", "price": 25.0, "unit": "元/斤", "category": "food"},
            {"item_name": "棉质T恤", "price": 89.0, "unit": "元/件", "category": "clothing"},
            {"item_name": "330ml啤酒", "price": 6.5, "unit": "元/瓶", "category": "beverage"},
            {"item_name": "500ml五粮液", "price": 1499.0, "unit": "元/瓶", "category": "beverage"},
            {"item_name": "月平均工资", "price": 12183.0, "unit": "元/月", "category": "income"},
            {"item_name": "理发", "price": 35.0, "unit": "元/次", "category": "service"},
        ],
    },
    "上海": {
        1990: [
            {"item_name": "梗米", "price": 0.9, "unit": "元/斤", "category": "food"},
            {"item_name": "大豆油", "price": 2.8, "unit": "元/升", "category": "food"},
            {"item_name": "精瘦肉", "price": 2.7, "unit": "元/斤", "category": "food"},
            {"item_name": "棉质T恤", "price": 20.0, "unit": "元/件", "category": "clothing"},
            {"item_name": "330ml啤酒", "price": 1.8, "unit": "元/瓶", "category": "beverage"},
            {"item_name": "500ml五粮液", "price": 108.0, "unit": "元/瓶", "category": "beverage"},
            {"item_name": "月平均工资", "price": 240.0, "unit": "元/月", "category": "income"},
            {"item_name": "理发", "price": 1.2, "unit": "元/次", "category": "service"},
        ],
        2024: [
            {"item_name": "梗米", "price": 6.5, "unit": "元/斤", "category": "food"},
            {"item_name": "大豆油", "price": 17.5, "unit": "元/升", "category": "food"},
            {"item_name": "精瘦肉", "price": 28.0, "unit": "元/斤", "category": "food"},
            {"item_name": "棉质T恤", "price": 99.0, "unit": "元/件", "category": "clothing"},
            {"item_name": "330ml啤酒", "price": 7.0, "unit": "元/瓶", "category": "beverage"},
            {"item_name": "500ml五粮液", "price": 1599.0, "unit": "元/瓶", "category": "beverage"},
            {"item_name": "月平均工资", "price": 12486.0, "unit": "元/月", "category": "income"},
            {"item_name": "理发", "price": 38.0, "unit": "元/次", "category": "service"},
        ]
    },
}
