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
    "上海": {"city_name": "上海", "coli_index": 100.0, "median_income": 7800.0, "province": "上海市"},
    "北京": {"city_name": "北京", "coli_index": 98.0, "median_income": 7500.0, "province": "北京市"},
    "深圳": {"city_name": "深圳", "coli_index": 95.0, "median_income": 7200.0, "province": "广东省"},
    "郑州": {"city_name": "郑州", "coli_index": 65.0, "median_income": 3500.0, "province": "河南省"},
    "开封": {"city_name": "开封", "coli_index": 52.0, "median_income": 2800.0, "province": "河南省"},
    "鹤岗": {"city_name": "鹤岗", "coli_index": 30.0, "median_income": 1800.0, "province": "黑龙江省"},
    "广州": {"city_name": "广州", "coli_index": 92.0, "median_income": 6900.0, "province": "广东省"},
    "杭州": {"city_name": "杭州", "coli_index": 88.0, "median_income": 6800.0, "province": "浙江省"},
    "成都": {"city_name": "成都", "coli_index": 72.0, "median_income": 4700.0, "province": "四川省"},
    "武汉": {"city_name": "武汉", "coli_index": 74.0, "median_income": 4800.0, "province": "湖北省"},
    "西安": {"city_name": "西安", "coli_index": 70.0, "median_income": 4300.0, "province": "陕西省"},
    "南京": {"city_name": "南京", "coli_index": 84.0, "median_income": 6200.0, "province": "江苏省"},
    "重庆": {"city_name": "重庆", "coli_index": 68.0, "median_income": 4200.0, "province": "重庆市"},
}

FALLBACK_CITY_PRICES: Dict[str, Dict[int, List[dict]]] = {
    "北京": {
        1990: [
            {"item_name": "猪肉", "price": 2.5},
            {"item_name": "大米", "price": 0.8},
            {"item_name": "鸡蛋", "price": 1.2},
        ],
        2024: [
            {"item_name": "猪肉", "price": 25.0},
            {"item_name": "大米", "price": 6.0},
            {"item_name": "鸡蛋", "price": 12.0},
        ],
    },
    "上海": {
        2024: [
            {"item_name": "猪肉", "price": 28.0},
            {"item_name": "大米", "price": 6.5},
            {"item_name": "鸡蛋", "price": 13.0},
        ]
    },
}
