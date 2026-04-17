from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from supabase import create_client, Client
from services.calculator import Calculator
from services.ai_service import AIService

class Settings(BaseSettings):
    """应用配置"""
    APP_NAME: str = "钱值时光机"
    APP_VERSION: str = "v1.0.0"
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    model_config = ConfigDict(env_file=".env")

settings = Settings()


# Supabase 客户端初始化
supabase: Client = None

def init_supabase():
    """初始化 Supabase 客户端"""
    global supabase
    supabase = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )

# 初始化 Supabase 客户端
init_supabase()

# 初始化服务
calculator = Calculator(supabase)
ai_service = AIService()

# 依赖项，用于获取 Supabase 客户端
def get_supabase():
    yield supabase

# 数据模型
class ConvertRequest(BaseModel):
    """货币购买力转换请求"""
    amount: float = Field(..., gt=0, description="转换金额，必须大于0")
    source_year: int = Field(..., ge=1980, le=2025, description="起始年份，1980-2025")
    city: str = Field(..., min_length=1, max_length=50, description="城市名称")
    
    @field_validator('city')
    def validate_city(cls, v):
        """验证城市名称"""
        valid_cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "西安", "南京", "重庆"]
        if v not in valid_cities:
            raise ValueError(f"城市名称无效，支持的城市: {', '.join(valid_cities)}")
        return v

class Item(BaseModel):
    """商品信息"""
    name: str
    price_then: float
    price_now: float
    purchasing_power: str

class ConvertResponse(BaseModel):
    """货币购买力转换响应"""
    equivalent_amount: float
    items: List[Item]
    ai_comment: str

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于宏观经济数据与AI语义理解的货币购买力时空坐标系"
)

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 测试 Supabase 连接
        result = supabase.table("macro_economics").select("year").limit(1).execute()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "database_status": db_status
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用钱值时光机API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.post("/api/v1/convert", response_model=ConvertResponse)
async def convert_purchasing_power(request: ConvertRequest):
    """
    货币购买力转换接口
    
    Args:
        request: 转换请求，包含金额、起始年份和城市名称
        
    Returns:
        转换结果，包含等价值、商品对比和AI评价
    """
    try:
        # 计算等价值
        equivalent_amount = calculator.calculate_equivalent_value(
            request.amount, 
            request.source_year, 
            2024
        )
        
        if equivalent_amount is None:
            raise HTTPException(
                status_code=500, 
                detail="无法计算货币购买力等价值，请检查数据是否完整"
            )
        
        # 获取实物价格数据
        city_prices = calculator.get_city_prices(request.city, request.source_year)
        
        # 构建商品对比列表
        items = []
        
        if city_prices and len(city_prices) >= 3:
            # 使用数据库中的数据
            for price_data in city_prices[:3]:  # 限制为3个商品
                # 获取当前年份的价格
                current_prices = calculator.get_city_prices(request.city, 2024)
                current_price = None
                
                if current_prices:
                    for current in current_prices:
                        if current.get("item_name") == price_data.get("item_name"):
                            current_price = current.get("price")
                            break
                
                if current_price:
                    items.append({
                        "name": price_data.get("item_name", "未知商品"),
                        "price_then": price_data.get("price", 0),
                        "price_now": current_price,
                        "purchasing_power": ""
                    })
        
        # 如果数据不足，使用默认商品数据
        if len(items) < 3:
            default_items = [
                {"name": "猪肉", "price_then": 2.5, "price_now": 25.0},
                {"name": "大米", "price_then": 0.8, "price_now": 6.0},
                {"name": "鸡蛋", "price_then": 1.2, "price_now": 12.0}
            ]
            
            # 只添加缺少的商品
            existing_names = {item["name"] for item in items}
            for default_item in default_items:
                if default_item["name"] not in existing_names and len(items) < 3:
                    items.append(default_item.copy())
        
        # 计算购买力对比
        comparison_results = calculator.calculate_purchasing_power_comparison(
            items, 
            request.source_year, 
            2024
        )
        
        # 生成AI评价
        ai_comment = ai_service.generate_comment(
            request.source_year, 
            request.amount, 
            equivalent_amount
        )
        
        if not ai_comment:
            ai_comment = ai_service.generate_fallback_comment(
                request.source_year, 
                request.amount, 
                equivalent_amount
            )
        
        return {
            "equivalent_amount": equivalent_amount,
            "items": comparison_results,
            "ai_comment": ai_comment
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")
