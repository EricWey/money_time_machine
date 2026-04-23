#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
货币购买力计算器
功能：根据宏观经济数据计算不同年份货币的购买力变化
"""

import logging
import random
from typing import Optional, Dict, Any

try:
    from supabase import Client
except ImportError:  # pragma: no cover
    Client = Any

from services.fallback_data import FALLBACK_CITY_PRICES, FALLBACK_MACRO_DATA
from services.item_metadata import get_item_metadata

logger = logging.getLogger(__name__)

class Calculator:
    """货币购买力计算器"""
    
    def __init__(self, supabase: Optional[Client]):
        """初始化计算器"""
        self.supabase = supabase
    
    def get_macro_data(self, year: int) -> Optional[Dict[str, Any]]:
        """
        获取指定年份的宏观经济数据
        
        Args:
            year: 年份
            
        Returns:
            包含宏观经济数据的字典，如果查询失败返回None
        """
        if not self.supabase:
            return FALLBACK_MACRO_DATA.get(year)

        try:
            result = self.supabase.table("macro_economics").select("*").eq("year", year).execute()
            if result.data:
                return result.data[0]
            else:
                logger.warning(f"未找到 {year} 年的宏观经济数据")
                return None
        except Exception as e:
            logger.error(f"获取 {year} 年宏观经济数据时出错: {str(e)}")
            return None
    
    def calculate_equivalent_value(self, amount: float, source_year: int, target_year: int = 2025) -> Optional[float]:
        """
        计算货币购买力等价值
        
        Args:
            amount: 原始金额
            source_year: 起始年份
            target_year: 目标年份，默认为2025年
            
        Returns:
            等价值，计算失败返回None
        """
        # 获取起始年和目标年的宏观经济数据
        source_data = self.get_macro_data(source_year)
        target_data = self.get_macro_data(target_year)
        
        if not source_data or not target_data:
            logger.error(f"无法获取 {source_year} 或 {target_year} 年的宏观经济数据")
            return None
        
        try:
            # 计算CPI比率
            cpi_ratio = round(target_data["cpi_index"] / source_data["cpi_index"], 4)
            
            # 计算M2调整值比率（累乘积）
            m2_adj_ratio = self.calculate_m2_adj_ratio(source_year, target_year)
            
            # 计算房产指数比率
            property_ratio = round(target_data["property_index_nat"] / source_data["property_index_nat"], 4)
            
            # 计算综合等价值
            equivalent_value = amount * (0.4 * cpi_ratio + 0.4 * m2_adj_ratio + 0.2 * property_ratio)
            
            logger.info(f"计算 {source_year} 年 {amount} 元到 {target_year} 年的等价值")
            logger.info(f"CPI比率: {cpi_ratio}, M2调整值比率: {m2_adj_ratio}, 房产指数比率: {property_ratio}")
            logger.info(f"等价值: {equivalent_value}")
            
            return round(equivalent_value, 2)
            
        except Exception as e:
            logger.error(f"计算等价值时出错: {str(e)}")
            return None
    
    def calculate_m2_adj_ratio(self, source_year: int, target_year: int) -> float:
        """
        计算M2调整值比率（累乘积）
        
        Args:
            source_year: 起始年份
            target_year: 目标年份
            
        Returns:
            M2调整值比率
        """
        try:
            if not self.supabase:
                yearly_data = [
                    FALLBACK_MACRO_DATA[year]
                    for year in sorted(FALLBACK_MACRO_DATA)
                    if source_year <= year <= target_year
                ]
                if not yearly_data:
                    return 1.0

                m2_adj_ratio = 1.0
                for data in yearly_data:
                    m2_adj_ratio *= (1 + data["m2_adj"] / 100)
                return round(m2_adj_ratio, 6)

            # 获取起始年到目标年之间的所有数据
            result = self.supabase.table("macro_economics").select("year", "m2_adj").gte("year", source_year).lte("year", target_year).execute()
            
            if not result.data:
                logger.error(f"无法获取 {source_year} 到 {target_year} 年之间的M2调整值数据")
                return 1.0
            
            # 计算累乘积
            m2_adj_ratio = 1.0
            for data in sorted(result.data, key=lambda item: item["year"]):
                m2_adj_ratio *= (1 + data["m2_adj"] / 100)
            
            return round(m2_adj_ratio, 6)
            
        except Exception as e:
            logger.error(f"计算M2调整值比率时出错: {str(e)}")
            return 1.0
    
    def get_city_prices(self, city: str, year: int) -> Optional[list]:
        """
        获取指定城市和年份的实物价格数据
        
        Args:
            city: 城市名称
            year: 年份
            
        Returns:
            实物价格数据列表，查询失败返回None
        """
        if not self.supabase:
            return FALLBACK_CITY_PRICES.get(city, {}).get(year)

        try:
            result = self.supabase.table("city_prices").select("*").eq("city_name", city).eq("year", year).execute()
            if result.data:
                return result.data
        except Exception as e:
            logger.warning(f"按 city_name 查询 {city} {year} 年实物价格失败，尝试使用 city_id 查询: {str(e)}")

        try:
            city_data = self.supabase.table("city_data").select("city_id").eq("city_name", city).limit(1).execute()
            if city_data.data:
                city_id = city_data.data[0]["city_id"]
                result = self.supabase.table("city_prices").select("*").eq("city_id", city_id).eq("year", year).execute()
                if result.data:
                    return result.data
        except Exception as e:
            logger.error(f"获取 {city} {year} 年实物价格数据时出错: {str(e)}")

        fallback_prices = FALLBACK_CITY_PRICES.get(city, {}).get(year)
        if fallback_prices:
            return fallback_prices

        logger.warning(f"未找到 {city} {year} 年的实物价格数据")
        return None
    
    def calculate_purchasing_power_comparison(self, items: list, source_year: int, target_year: int = 2024) -> list:
        """
        计算购买力对比
        
        Args:
            items: 商品列表
            source_year: 起始年份
            target_year: 目标年份
            
        Returns:
            购买力对比结果列表
        """
        comparison_results = []
        
        for item in items:
            try:
                price_then = item.get("price_then", 0)
                price_now = item.get("price_now", 0)
                
                if price_then > 0 and price_now > 0:
                    change_percent = ((price_now - price_then) / price_then) * 100
                    
                    if change_percent > 0:
                        purchasing_power = f"上涨 {abs(change_percent):.1f}%"
                    elif change_percent < 0:
                        purchasing_power = f"下降 {abs(change_percent):.1f}%"
                    else:
                        purchasing_power = "保持不变"
                else:
                    purchasing_power = "无法计算"
                
                comparison_results.append({
                    "name": item.get("name", "未知商品"),
                    "unit": item.get("unit"),
                    "category": item.get("category"),
                    "note": item.get("note"),
                    "price_then": price_then,
                    "price_now": price_now,
                    "purchasing_power": purchasing_power
                })
                
            except Exception as e:
                logger.error(f"计算商品购买力对比时出错: {str(e)}")
                continue
        
        return comparison_results

    def build_random_item_comparison_set(self, city: str, source_year: int, target_year: int = 2024, sample_size: int = 3) -> list:
        """
        构建随机商品对比集合。
        仅从起始年份与目标年份都存在价格的商品中抽样。
        """
        source_prices = self.get_city_prices(city, source_year) or []
        target_prices = self.get_city_prices(city, target_year) or []

        target_map = {
            item.get("item_name"): item
            for item in target_prices
            if item.get("item_name") and item.get("price") is not None
        }

        candidates = []
        for source_item in source_prices:
            item_name = source_item.get("item_name")
            if not item_name:
                continue

            target_item = target_map.get(item_name)
            if not target_item:
                continue

            metadata = get_item_metadata(item_name)
            candidates.append({
                "name": item_name,
                "unit": source_item.get("unit") or target_item.get("unit") or metadata.get("unit"),
                "category": source_item.get("category") or target_item.get("category") or metadata.get("category"),
                "note": metadata.get("note"),
                "price_then": source_item.get("price", 0),
                "price_now": target_item.get("price", 0),
            })

        if len(candidates) <= sample_size:
            return candidates

        return random.sample(candidates, sample_size)
