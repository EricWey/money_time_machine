#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
城市基础数据初始化脚本
功能：将城市基础数据注入Supabase数据库的city_data表
"""

import os
import time
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
# 抑制HTTP客户端库的日志
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

load_dotenv()

class CityDataSeeder:
    """城市数据初始化器"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase: Client = None
        self.stats = {
            "total_records": 0,
            "new_records": 0,
            "updated_records": 0,
            "errors": 0
        }
        self.start_time = None

        self.init_supabase()

    def init_supabase(self):
        """初始化Supabase客户端"""
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase连接信息未配置，请检查.env文件")

        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase客户端初始化成功")
        except Exception as e:
            raise Exception(f"Supabase客户端初始化失败: {str(e)}")

    def validate_city_data(self, city_data: dict) -> bool:
        """
        验证城市数据的合理性

        Args:
            city_data: 城市数据字典

        Returns:
            验证是否通过
        """
        try:
            coli_index = city_data.get("coli_index")
            median_income = city_data.get("median_income")

            if not (20 <= coli_index <= 120):
                logger.warning(f"城市 {city_data.get('city_name')} 的COLI指数 {coli_index} 超出合理范围 [20, 120]")
                return False

            if not (1000 <= median_income <= 100000):
                logger.warning(f"城市 {city_data.get('city_name')} 的中位数收入 {median_income} 超出合理范围 [1000, 100000]")
                return False

            return True
        except Exception as e:
            logger.error(f"验证城市数据时出错: {str(e)}")
            return False

    def get_city_list(self) -> list:
        """
        获取城市列表数据

        Returns:
            城市数据列表
        """
        raw_city_data = [
            ("北京", "北京市", 98.00, 7800, 1),
            ("上海", "上海市", 100.00, 8100, 1),
            ("天津", "天津市", 79.00, 5600, 1),
            ("重庆", "重庆市", 72.00, 4600, 1),
            ("石家庄", "河北省", 63.00, 4200, 2),
            ("太原", "山西省", 64.00, 4300, 2),
            ("呼和浩特", "内蒙古自治区", 62.00, 4100, 2),
            ("沈阳", "辽宁省", 68.00, 4700, 2),
            ("长春", "吉林省", 63.00, 4200, 2),
            ("哈尔滨", "黑龙江省", 65.00, 4300, 2),
            ("南京", "江苏省", 84.00, 6500, 1),
            ("杭州", "浙江省", 88.00, 7100, 1),
            ("合肥", "安徽省", 66.00, 4600, 2),
            ("福州", "福建省", 69.00, 4700, 2),
            ("南昌", "江西省", 64.00, 4300, 2),
            ("济南", "山东省", 67.00, 4600, 2),
            ("郑州", "河南省", 65.00, 4400, 2),
            ("武汉", "湖北省", 74.00, 5000, 2),
            ("长沙", "湖南省", 69.00, 4700, 2),
            ("广州", "广东省", 92.00, 7300, 1),
            ("南宁", "广西壮族自治区", 60.00, 4000, 2),
            ("海口", "海南省", 66.00, 4200, 2),
            ("成都", "四川省", 72.00, 4900, 2),
            ("贵阳", "贵州省", 58.00, 3900, 2),
            ("昆明", "云南省", 61.00, 4100, 2),
            ("拉萨", "西藏自治区", 67.00, 4400, 2),
            ("西安", "陕西省", 70.00, 4600, 2),
            ("兰州", "甘肃省", 60.00, 4000, 2),
            ("西宁", "青海省", 59.00, 3900, 2),
            ("银川", "宁夏回族自治区", 58.00, 3900, 2),
            ("乌鲁木齐", "新疆维吾尔自治区", 65.00, 4300, 2),
        ]

        return [
            {
                "city_name": city_name,
                "province": province,
                "coli_index": coli_index,
                "median_income": median_income,
                "region_level": region_level
            }
            for city_name, province, coli_index, median_income, region_level in raw_city_data
        ]

    def check_city_exists(self, city_name: str) -> bool:
        """
        检查城市数据是否已存在

        Args:
            city_name: 城市名称

        Returns:
            是否存在
        """
        try:
            result = self.supabase.table("city_data").select("city_name").eq("city_name", city_name).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"检查城市 {city_name} 是否存在时出错: {str(e)}")
            return False

    def seed_city_data(self):
        """执行城市数据注入"""
        logger.info("开始城市数据注入...")

        city_list = self.get_city_list()
        self.stats["total_records"] = len(city_list)

        for city_data in city_list:
            city_name = city_data["city_name"]

            try:
                if not self.validate_city_data(city_data):
                    self.stats["errors"] += 1
                    logger.error(f"城市 {city_name} 数据验证失败，跳过插入")
                    continue

                existing = self.check_city_exists(city_name)

                if existing:
                    result = self.supabase.table("city_data").update(city_data).eq("city_name", city_name).execute()
                    if result.data:
                        self.stats["updated_records"] += 1
                        logger.info(f"更新城市 {city_name} 数据成功")
                else:
                    result = self.supabase.table("city_data").insert(city_data).execute()
                    if result.data:
                        self.stats["new_records"] += 1
                        logger.info(f"插入城市 {city_name} 数据成功")

            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"处理城市 {city_name} 数据时出错: {str(e)}")

        logger.info(f"城市数据注入完成")

    def print_statistics(self):
        """打印统计信息"""
        logger.info("\n=== 城市数据注入统计信息 ===")
        logger.info(f"总记录数: {self.stats['total_records']}")
        logger.info(f"新增记录数: {self.stats['new_records']}")
        logger.info(f"更新记录数: {self.stats['updated_records']}")
        logger.info(f"错误记录数: {self.stats['errors']}")

        end_time = time.time()
        execution_time = round(end_time - self.start_time, 2)
        logger.info(f"执行时间: {execution_time} 秒")

        if self.stats["errors"] == 0:
            logger.info("\n城市基础数据已成功装载！")
        else:
            logger.warning(f"\n数据注入完成，但存在 {self.stats['errors']} 个错误")

    def run(self):
        """运行整个流程"""
        self.start_time = time.time()
        logger.info("开始执行城市数据初始化流程")

        try:
            self.seed_city_data()
            self.print_statistics()

        except Exception as e:
            logger.error(f"执行过程中出错: {str(e)}")
            raise

if __name__ == "__main__":
    seeder = CityDataSeeder()
    seeder.run()
