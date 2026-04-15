#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国宏观经济数据注入脚本
功能：将1980-2025年宏观经济数据注入Supabase数据库
"""

import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
# 抑制HTTP客户端库的日志
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

# 加载环境变量
load_dotenv()

class MacroDataInjector:
    """宏观经济数据注入器"""
    
    def __init__(self):
        """初始化数据注入器"""
        # Supabase连接配置
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase: Client = None
        
        # 初始化数据存储
        self.macro_data = []
        self.stats = {
            "total_records": 0,
            "new_records": 0,
            "updated_records": 0,
            "errors": 0
        }
        
        # 基准年份和CPI基准值
        self.base_year = 1980
        self.base_cpi = 100.0
        
        # 记录执行时间
        self.start_time = None
        
        # 初始化Supabase客户端
        self.init_supabase()
    
    def init_supabase(self):
        """初始化Supabase客户端"""
        if not self.supabase_url or not self.supabase_key:
            error_msg = "Supabase连接信息未配置，请检查.env文件"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase客户端初始化成功")
            # 验证连接
            self.verify_connection()
        except Exception as e:
            error_msg = f"Supabase客户端初始化失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def verify_connection(self):
        """验证Supabase连接"""
        try:
            # 尝试执行一个简单的查询来验证连接
            result = self.supabase.table("macro_economics").select("year").limit(1).execute()
            logger.info("Supabase连接验证成功")
        except Exception as e:
            error_msg = f"Supabase连接验证失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def clear_existing_data(self):
        """清除现有数据"""
        try:
            logger.info("开始清除现有数据...")
            # 使用neq('year', 0)来删除所有记录，因为年份不可能为0
            result = self.supabase.table("macro_economics").delete().neq("year", 0).execute()
            logger.info(f"成功清除 {len(result.data)} 条记录")
        except Exception as e:
            error_msg = f"清除数据时出错: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def load_data_from_table(self):
        """从表格数据加载宏观经济数据"""
        logger.info("开始加载宏观经济数据...")
        
        # 从表格数据提取的原始数据
        # 格式：[(年份, CPI同比, M2增速, GDP增速, 房产指数参考)]
        raw_data = [
            # 1980-1984
            (1980, 6.0, 19.0, 7.9, 100),
            (1981, 2.4, 14.5, 5.1, 105),
            (1982, 1.9, 13.0, 9.0, 110),
            (1983, 1.5, 12.0, 10.8, 112),
            (1984, 2.8, 20.0, 15.2, 115),
            # 1985-1989
            (1985, 9.3, 24.5, 13.5, 120),
            (1986, 6.5, 29.0, 8.9, 125),
            (1987, 7.3, 24.0, 11.7, 130),
            (1988, 18.8, 21.0, 11.3, 133),
            (1989, 18.0, 15.0, 4.2, 135),
            # 1990-1994
            (1990, 3.1, 20.2, 3.9, 140),
            (1991, 3.4, 26.5, 9.3, 150),
            (1992, 6.4, 31.3, 14.2, 160),
            (1993, 14.7, 37.3, 13.9, 170),
            (1994, 24.1, 34.5, 13.0, 180),
            # 1995-1999
            (1995, 17.1, 29.5, 10.9, 185),
            (1996, 8.3, 25.3, 9.9, 190),
            (1997, 2.8, 19.6, 9.2, 195),
            (1998, -0.8, 15.3, 7.8, 200),
            (1999, -1.4, 14.7, 7.7, 210),
            # 2000-2004
            (2000, 0.4, 12.3, 8.5, 220),
            (2001, 0.7, 14.4, 8.3, 240),
            (2002, -0.8, 16.8, 9.1, 260),
            (2003, 1.2, 19.6, 10.0, 280),
            (2004, 3.9, 14.6, 10.1, 300),
            # 2005-2009
            (2005, 1.8, 17.6, 11.4, 320),
            (2006, 1.5, 16.9, 12.7, 350),
            (2007, 4.8, 16.7, 14.2, 380),
            (2008, 5.9, 17.8, 9.6, 420),
            (2009, -0.7, 27.7, 9.4, 450),
            # 2010-2014
            (2010, 3.3, 19.7, 10.6, 500),
            (2011, 5.4, 13.6, 9.6, 550),
            (2012, 2.6, 13.8, 7.9, 600),
            (2013, 2.6, 13.6, 7.8, 630),
            (2014, 2.0, 12.2, 7.4, 650),
            # 2015-2019
            (2015, 1.4, 13.3, 7.0, 700),
            (2016, 2.0, 11.3, 6.8, 780),
            (2017, 1.6, 8.1, 6.9, 850),
            (2018, 2.1, 8.1, 6.7, 900),
            (2019, 2.9, 8.7, 6.0, 950),
            # 2020-2025
            (2020, 2.5, 10.1, 2.2, 1000),
            (2021, 0.9, 9.0, 8.4, 1050),
            (2022, 2.0, 11.8, 3.0, 1020),
            (2023, 0.2, 9.7, 5.2, 1000),
            (2024, 0.2, 8.7, 5.0, 990),
            (2025, 0.8, 8.0, 5.0, 980)
        ]
        
        # 计算CPI指数和M2调整值
        current_cpi = self.base_cpi
        
        for year, cpi_rate, m2_growth, gdp_growth, property_index in raw_data:
            # 计算CPI指数（链式累积）
            if year > self.base_year:
                current_cpi *= (1 + cpi_rate / 100)
            cpi_index = round(current_cpi, 4)
            
            # 计算M2调整值（M2增速 - GDP增速）
            m2_adj = round(m2_growth - gdp_growth, 4)
            
            # 标记2025年为预测数据
            is_forecast = year == 2025
            
            # 构建数据字典
            data = {
                "year": year,
                "cpi_index": cpi_index,
                "m2_growth": m2_growth,
                "gdp_growth": gdp_growth,
                "m2_adj": m2_adj,
                "property_index_nat": property_index,
                "is_forecast": is_forecast
            }
            
            # 添加到数据列表
            self.macro_data.append(data)
            
        self.stats["total_records"] = len(self.macro_data)
        logger.info(f"数据加载完成，共加载 {self.stats['total_records']} 条记录")
    
    def insert_or_update_data(self):
        """插入或更新数据"""
        logger.info("开始插入/更新数据...")
        
        for data in self.macro_data:
            year = data["year"]
            
            try:
                # 检查数据是否已存在
                existing = self.supabase.table("macro_economics").select("year").eq("year", year).execute()
                
                if len(existing.data) > 0:
                    # 更新现有记录
                    result = self.supabase.table("macro_economics").update(data).eq("year", year).execute()
                    if result.data:
                        self.stats["updated_records"] += 1
                        logger.info(f"更新 {year} 年数据成功")
                    else:
                        self.stats["errors"] += 1
                        logger.error(f"更新 {year} 年数据失败")
                else:
                    # 插入新记录
                    result = self.supabase.table("macro_economics").insert(data).execute()
                    if result.data:
                        self.stats["new_records"] += 1
                        if year % 5 == 0:
                            logger.info(f"插入 {year} 年数据成功")
                    else:
                        self.stats["errors"] += 1
                        logger.error(f"插入 {year} 年数据失败")
            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"处理 {year} 年数据时出错: {str(e)}")
    
    def calculate_cpi_equivalent(self, base_year, target_year, amount=100):
        """计算不同年份的CPI等价金额"""
        base_data = next((d for d in self.macro_data if d["year"] == base_year), None)
        target_data = next((d for d in self.macro_data if d["year"] == target_year), None)
        
        if not base_data or not target_data:
            logger.error(f"找不到 {base_year} 或 {target_year} 年的CPI数据")
            return None
        
        base_cpi = base_data["cpi_index"]
        target_cpi = target_data["cpi_index"]
        equivalent = amount * (target_cpi / base_cpi)
        return round(equivalent, 2)
    
    def get_m2_adj_by_year(self, year):
        """获取指定年份的M2调整值"""
        data = next((d for d in self.macro_data if d["year"] == year), None)
        if data:
            return data["m2_adj"]
        else:
            logger.error(f"找不到 {year} 年的M2调整值数据")
            return None
    
    def validate_data(self):
        """验证数据"""
        logger.info("开始数据验证...")
        
        # 检查年份完整性
        years = sorted([d["year"] for d in self.macro_data])
        expected_years = list(range(1980, 2026))
        
        if years == expected_years:
            logger.info("年份完整性验证通过，无缺失年份")
        else:
            missing_years = [y for y in expected_years if y not in years]
            logger.error(f"年份完整性验证失败，缺失年份: {missing_years}")
        
        # 验证1980年CPI指数为100
        base_year_data = next((d for d in self.macro_data if d["year"] == 1980), None)
        if base_year_data and base_year_data["cpi_index"] == 100.0:
            logger.info("1980年CPI基准值验证通过")
        else:
            logger.error("1980年CPI基准值验证失败")
        
        # 验证2025年标记为预测数据
        year_2025_data = next((d for d in self.macro_data if d["year"] == 2025), None)
        if year_2025_data and year_2025_data["is_forecast"]:
            logger.info("2025年预测数据标记验证通过")
        else:
            logger.error("2025年预测数据标记验证失败")
    
    def print_validation_info(self):
        """打印验证信息"""
        logger.info("\n=== 数据验证信息 ===")
        
        # 计算1980年100元在2024年的等价金额
        equivalent_2024 = self.calculate_cpi_equivalent(1980, 2024, 100)
        if equivalent_2024:
            logger.info(f"1980年 100元 在 2024年 相当于 {equivalent_2024} 元")
        
        # 获取2009年4万亿计划时期的M2调整值
        m2_adj_2009 = self.get_m2_adj_by_year(2009)
        if m2_adj_2009:
            logger.info(f"2009年 4万亿计划时期，M2_adj 的数值是 {m2_adj_2009}%")
    
    def print_statistics(self):
        """打印统计信息"""
        logger.info("\n=== 数据注入统计信息 ===")
        logger.info(f"总记录数: {self.stats['total_records']}")
        logger.info(f"新增记录数: {self.stats['new_records']}")
        logger.info(f"更新记录数: {self.stats['updated_records']}")
        logger.info(f"错误记录数: {self.stats['errors']}")
        
        # 计算执行时间
        end_time = time.time()
        execution_time = round(end_time - self.start_time, 2)
        logger.info(f"执行时间: {execution_time} 秒")
    
    def run(self):
        """运行整个流程"""
        self.start_time = time.time()
        logger.info("开始执行宏观经济数据注入流程")
        
        try:
            # 清除现有数据
            self.clear_existing_data()
            
            # 加载数据
            self.load_data_from_table()
            
            # 验证数据
            self.validate_data()
            
            # 插入或更新数据
            self.insert_or_update_data()
            
            # 打印验证信息
            self.print_validation_info()
            
            # 打印统计信息
            self.print_statistics()
            
            if self.stats["errors"] == 0:
                logger.info("\n1980-2025 权威宏观数据已成功装载至时光机！")
            else:
                logger.warning(f"\n数据注入完成，但存在 {self.stats['errors']} 个错误")
                
        except Exception as e:
            logger.error(f"执行过程中出错: {str(e)}")
            raise

if __name__ == "__main__":
    # 运行数据注入流程
    injector = MacroDataInjector()
    injector.run()