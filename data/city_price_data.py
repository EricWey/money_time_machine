import pandas as pd
import numpy as np
import os
import time
import logging
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

# ==========================================
# 1. 城市精密配置表 (基于 2026 年最新历史追溯逻辑)
# ==========================================
# anchor: 参照系 (北京-北方/内陆, 上海-南方/沿海, 广州-华南, 成都-西南)
# s_inc: 收入/服务系数 (反映工资和理发水平)
# s_food: 食品系数 (反映米油肉水平)
city_configs = {
    "001": {"name": "北京", "anchor": "北京", "s_inc": 1.00, "s_food": 1.00},
    "002": {"name": "上海", "anchor": "上海", "s_inc": 1.00, "s_food": 1.00},
    "003": {"name": "天津", "anchor": "北京", "s_inc": 0.88, "s_food": 0.98},
    "004": {"name": "重庆", "anchor": "成都", "s_inc": 0.82, "s_food": 0.92},
    "005": {"name": "石家庄", "anchor": "北京", "s_inc": 0.72, "s_food": 0.95},
    "006": {"name": "太原", "anchor": "北京", "s_inc": 0.70, "s_food": 0.94},
    "007": {"name": "呼和浩特", "anchor": "北京", "s_inc": 0.75, "s_food": 0.96},
    "008": {"name": "沈阳", "anchor": "北京", "s_inc": 0.74, "s_food": 0.94},
    "009": {"name": "长春", "anchor": "北京", "s_inc": 0.70, "s_food": 0.92},
    "010": {"name": "哈尔滨", "anchor": "北京", "s_inc": 0.70, "s_food": 0.92},
    "011": {"name": "南京", "anchor": "上海", "s_inc": 0.88, "s_food": 0.98},
    "012": {"name": "杭州", "anchor": "上海", "s_inc": 0.92, "s_food": 0.98},
    "013": {"name": "合肥", "anchor": "上海", "s_inc": 0.78, "s_food": 0.95},
    "014": {"name": "福州", "anchor": "上海", "s_inc": 0.82, "s_food": 0.96},
    "015": {"name": "南昌", "anchor": "上海", "s_inc": 0.72, "s_food": 0.94},
    "016": {"name": "济南", "anchor": "北京", "s_inc": 0.78, "s_food": 0.96},
    "017": {"name": "郑州", "anchor": "北京", "s_inc": 0.75, "s_food": 0.95},
    "018": {"name": "武汉", "anchor": "上海", "s_inc": 0.82, "s_food": 0.95},
    "019": {"name": "长沙", "anchor": "上海", "s_inc": 0.80, "s_food": 0.94},
    "020": {"name": "广州", "anchor": "广州", "s_inc": 0.95, "s_food": 1.02},
    "021": {"name": "南宁", "anchor": "广州", "s_inc": 0.70, "s_food": 0.96},
    "022": {"name": "海口", "anchor": "广州", "s_inc": 0.72, "s_food": 1.12}, # 离岛物流贵
    "023": {"name": "成都", "anchor": "成都", "s_inc": 0.82, "s_food": 0.92},
    "024": {"name": "贵阳", "anchor": "成都", "s_inc": 0.68, "s_food": 0.94},
    "025": {"name": "昆明", "anchor": "成都", "s_inc": 0.72, "s_food": 0.95},
    "026": {"name": "拉萨", "anchor": "北京", "s_inc": 0.78, "s_food": 1.25}, # 极端物流
    "027": {"name": "西安", "anchor": "北京", "s_inc": 0.76, "s_food": 0.95},
    "028": {"name": "兰州", "anchor": "北京", "s_inc": 0.68, "s_food": 0.96},
    "029": {"name": "西宁", "anchor": "北京", "s_inc": 0.68, "s_food": 0.98},
    "030": {"name": "银川", "anchor": "北京", "s_inc": 0.70, "s_food": 0.96},
    "031": {"name": "乌鲁木齐", "anchor": "北京", "s_inc": 0.75, "s_food": 1.10}
}

class PriceDataSeeder:
    """价格数据初始化器"""

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

    def generate_master_data(self, truth_file, cpi_file):
        # 加载已有的北京、上海真值
        anchors_df = pd.read_csv(truth_file)
        # 加载各省 CPI 数据 (要求格式: year, city_name, cpi_value)
        # cpi_value 应该是同比指数，如 105.2 代表上涨 5.2%
        cpi_df = pd.read_csv(cpi_file)
        # 处理CPI数据中的空值，设置为100
        cpi_df['cpi_value'] = pd.to_numeric(cpi_df['cpi_value'], errors='coerce').fillna(100)
        
        final_results = []
        record_id = 1  # 自增长ID
        
        for city_id, cfg in city_configs.items():
            city_name = cfg['name']
            anchor_city = cfg['anchor']
            
            logger.info(f"Processing: {city_name} (Anchor: {anchor_city})")
            
            # 获取锚点数据
            anchor_data = anchors_df[anchors_df['city_name'] == anchor_city]
         
            for year in range(1980, 2026):
                # 1. 计算 CPI 修正率
                # 逻辑：目标城市价格 = 锚点价格 * (目标累计CPI / 锚点累计CPI) * 地区初始偏差
                # 为了简化计算，我们直接使用当年的 CPI 相对强弱作为偏移修正
                try:
                    t_cpi = cpi_df[(cpi_df['year'] == year) & (cpi_df['city_name'] == city_name)]['cpi_value'].values[0]
                    a_cpi = cpi_df[(cpi_df['year'] == year) & (cpi_df['city_name'] == anchor_city)]['cpi_value'].values[0]
                    cpi_adj = t_cpi / a_cpi
                except:
                    cpi_adj = 1.0 # 缺失则默认同步
                  
                
                # 获取该年份所有商品
                year_items = anchor_data[anchor_data['year'] == year]
               
                for _, row in year_items.iterrows():
                    item = row['item_name']
                    cat = row['category']
                    base_p = row['price']
                    # 2. 应用分类 Scale Factor
                    if cat == 'income' or cat == 'service':
                        scale = cfg['s_inc']
                    elif item in ["500ml五粮液", "330ml罐装啤酒"]:
                        scale = 1.0 # 工业品和名酒全国趋同
                    else:
                        scale = cfg['s_food']
                    
                    # 3. 最终定价计算
                    # 加入微小随机扰动 (±2%) 增加数据真实感
                    noise = np.random.uniform(0.98, 1.02)
                    final_p = round(base_p * scale * cpi_adj * noise, 2)
    
                    # 添加自增长ID
                    final_results.append([
                        record_id, city_id, city_name, year, cat, item, 
                        final_p, row['unit'], row['is_essential']
                    ])
                    record_id += 1

        # 保存文件
        output_df = pd.DataFrame(final_results, columns=[
            "id", "city_id", "city_name", "year", "category", "item_name", "price", "unit", "is_essential"
        ])
        output_df.to_csv("data/city_price_data.csv", index=False, encoding="utf-8-sig")
        logger.info(f"生成CSV文件成功，共 {len(final_results)} 条记录")
        return output_df

    def seed_price_data(self, price_data_df):
        """执行价格数据注入"""
        logger.info("开始价格数据注入...")

        # 清空数据表，防止重复插入
        try:
            logger.info("清空city_prices表...")
            # 使用neq('id', '')来匹配所有记录，因为Supabase要求DELETE必须有WHERE子句
            delete_result = self.supabase.table("city_prices").delete().gte('year', 1980).execute()
            logger.info("表清空成功")
        except Exception as e:
            logger.error(f"清空表时出错: {str(e)}")

        self.stats["total_records"] = len(price_data_df)

        # 转换DataFrame为字典列表并处理nan值
        price_records = price_data_df.to_dict('records')
        processed_records = []
        
        for record in price_records:
            try:
                # 处理nan值，替换为None
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                processed_records.append(record)
            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"处理记录时出错: {str(e)}")
        
        # 批量插入数据，每批100条
        batch_size = 100
        total_batches = (len(processed_records) + batch_size - 1) // batch_size
        
        for i in range(0, len(processed_records), batch_size):
            batch = processed_records[i:i+batch_size]
            try:
                # 批量插入
                insert_result = self.supabase.table("city_prices").insert(batch).execute()
                if insert_result.data:
                    self.stats["new_records"] += len(insert_result.data)
                logger.info(f"批量插入第 {i//batch_size + 1}/{total_batches} 批，成功插入 {len(insert_result.data)} 条记录")
            except Exception as e:
                self.stats["errors"] += len(batch)
                logger.error(f"批量插入时出错: {str(e)}")

        logger.info(f"价格数据注入完成")

    def print_statistics(self):
        """打印统计信息"""
        logger.info("\n=== 价格数据注入统计信息 ===")
        logger.info(f"总记录数: {self.stats['total_records']}")
        logger.info(f"新增记录数: {self.stats['new_records']}")
        logger.info(f"更新记录数: {self.stats['updated_records']}")
        logger.info(f"错误记录数: {self.stats['errors']}")

        end_time = time.time()
        execution_time = round(end_time - self.start_time, 2)
        logger.info(f"执行时间: {execution_time} 秒")

        if self.stats["errors"] == 0:
            logger.info("\n价格数据已成功装载！")
        else:
            logger.warning(f"\n数据注入完成，但存在 {self.stats['errors']} 个错误")

    def run(self):
        """运行整个流程"""
        self.start_time = time.time()
        logger.info("开始执行价格数据初始化流程")

        try:
            # 使用指定的文件路径
            truth_file = "data/city_data_new.csv"
            cpi_file = "data/reformatted_cpi.csv"
            
            logger.info(f"加载数据文件: {truth_file} 和 {cpi_file}")
            price_data_df = self.generate_master_data(truth_file, cpi_file)
            self.seed_price_data(price_data_df)
            self.print_statistics()

        except Exception as e:
            logger.error(f"执行过程中出错: {str(e)}")
            raise

# ==========================================
# 3. 使用说明
# ==========================================
# 确保你有以下两个文件在目录下：
# 1. data/city_data_new.csv (北京上海的统计数据)
# 2. data/cpi.csv (各省CPI数据)
# 
# 运行方式：
# seeder = PriceDataSeeder()
# seeder.run()

if __name__ == "__main__":
    seeder = PriceDataSeeder()
    seeder.run()