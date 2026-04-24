import os
import logging
from typing import Optional, List, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

try:
    from supabase import create_client, Client
except ImportError:  # pragma: no cover
    create_client = None
    Client = Any

from services.ai_service import AIService
from services.calculator import Calculator

logger = logging.getLogger(__name__)
SUPPORTED_CITIES = {
    "北京", "上海", "天津", "重庆", "石家庄", "太原", "呼和浩特", "沈阳", "长春", "哈尔滨",
    "南京", "杭州", "合肥", "福州", "南昌", "济南", "郑州", "武汉", "长沙", "广州",
    "南宁", "海口", "成都", "贵阳", "昆明", "拉萨", "西安", "兰州", "西宁", "银川", "乌鲁木齐"
}

class Settings(BaseSettings):
    """应用配置"""
    APP_NAME: str = "钱值时光机"
    APP_VERSION: str = "v1.0.0"
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    model_config = ConfigDict(env_file=".env")

settings = Settings()


# Supabase 客户端初始化
supabase: Optional[Client] = None

def init_supabase():
    """初始化 Supabase 客户端"""
    global supabase
    if not create_client:
        logger.warning("supabase 包未安装，无法初始化真实数据源")
        supabase = None
        return

    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("未配置 Supabase 环境变量，无法初始化真实数据源")
        supabase = None
        return

    try:
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
    except Exception as exc:
        logger.warning("Supabase 初始化失败: %s", exc)
        supabase = None

# 初始化 Supabase 客户端
init_supabase()

# 初始化服务
calculator = Calculator(supabase)
ai_service = AIService()

# 数据模型
class ConvertRequest(BaseModel):
    """货币购买力转换请求"""
    amount: float = Field(..., gt=0, description="转换金额，必须大于0")
    source_year: int = Field(..., ge=1980, le=2025, description="起始年份，1980-2025")
    city: str = Field(..., min_length=1, max_length=50, description="城市名称")
    
    @field_validator('city')
    def validate_city(cls, v):
        """验证城市名称"""
        if v not in SUPPORTED_CITIES:
            raise ValueError(f"城市名称无效，支持的城市: {', '.join(sorted(SUPPORTED_CITIES))}")
        return v

class Item(BaseModel):
    """商品信息"""
    name: str
    unit: Optional[str] = None
    category: Optional[str] = None
    note: Optional[str] = None
    price_then: float
    price_now: float
    purchasing_power: str

class ConvertResponse(BaseModel):
    """货币购买力转换响应"""
    equivalent_amount: float
    items: List[Item]
    ai_comment: str

class DriftRequest(BaseModel):
    """财富漂流请求"""
    current_city: str = Field(..., min_length=1, max_length=50, description="当前所在城市")
    monthly_income: float = Field(..., gt=0, description="月收入金额，必须大于0")
    target_city: str = Field(..., min_length=1, max_length=50, description="目标迁移城市")

    @model_validator(mode="after")
    def validate_different_cities(self):
        if self.current_city == self.target_city:
            raise ValueError("当前城市和目标城市不能相同")
        return self

class DriftResponse(BaseModel):
    """财富漂流响应"""
    current_city: str
    target_city: str
    current_city_coli: float
    target_city_coli: float
    equivalent_amount: float
    target_city_median_income: float
    wealth_ratio: float
    identity_label: str
    city_comparison: str
    ai_essay: str

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
        db_status = "connected"
        if supabase:
            supabase.table("macro_economics").select("year").limit(1).execute()
        else:
            db_status = "disconnected"
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

@app.get("/api/v1/macro")
async def get_macro_data(
    year: Optional[int] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    sort: str = "year",
    order: str = "asc"
):
    """
    获取宏观经济数据

    Args:
        year: 特定年份
        start_year: 起始年份
        end_year: 结束年份
        limit: 返回数据条数限制
        offset: 数据偏移量
        sort: 排序字段
        order: 排序方向

    Returns:
        宏观经济数据列表
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Supabase 未初始化，真实宏观数据不可用")

        query = supabase.table("macro_economics").select("*")

        if year:
            query = query.eq("year", year)
        elif start_year and end_year:
            query = query.gte("year", start_year).lte("year", end_year)
        elif start_year:
            query = query.gte("year", start_year)
        elif end_year:
            query = query.lte("year", end_year)

        query = query.order(sort, ascending=order.lower() != "desc")
        query = query.limit(limit).offset(offset)
        result = query.execute()

        formatted_data = [
            {
                "year": item.get("year"),
                "cpi_index": item.get("cpi_index"),
                "m2_adj": item.get("m2_adj"),
                "property_index_nat": item.get("property_index_nat")
            }
            for item in (result.data or [])
        ]
        logger.info("从 Supabase 成功获取 %s 条宏观经济数据", len(formatted_data))
        return formatted_data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"获取宏观经济数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取宏观经济数据失败: {str(e)}")

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
        if not supabase:
            raise HTTPException(status_code=503, detail="Supabase 未初始化，真实转换接口不可用")

        # 计算等价值
        equivalent_amount = calculator.calculate_equivalent_value(
            request.amount, 
            request.source_year, 
            2024
        )
        
        if equivalent_amount is None:
            raise HTTPException(
                status_code=500, 
                detail="无法计算货币购买力等价值，请检查 Supabase 中的数据是否完整"
            )
        
        items = calculator.build_random_item_comparison_set(
            request.city,
            request.source_year,
            2024,
            sample_size=3
        )
        
        if len(items) < 3:
            raise HTTPException(status_code=500, detail="商品价格数据不足，无法生成完整对比结果")
        
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
            equivalent_amount,
            comparison_results
        )
        
        if not ai_comment:
            raise HTTPException(status_code=502, detail="AI 评价服务暂不可用")
        
        return {
            "equivalent_amount": equivalent_amount,
            "items": comparison_results,
            "ai_comment": ai_comment
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

def get_city_data(city_name: str) -> Optional[dict]:
    """
    获取城市数据

    Args:
        city_name: 城市名称

    Returns:
        城市数据字典，不存在返回None
    """
    if not supabase:
        return None

    try:
        result = supabase.table("city_data").select("*").eq("city_name", city_name).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        logger.error(f"获取城市 {city_name} 数据时出错: {str(e)}")
        return None

def calculate_wealth_ratio(equivalent_amount: float, median_income: float) -> float:
    """
    计算财富比率

    Args:
        equivalent_amount: 等值收入
        median_income: 中位数收入

    Returns:
        财富比率
    """
    if median_income <= 0:
        return 0.0
    return round(equivalent_amount / median_income, 2)

def get_identity_label(wealth_ratio: float) -> str:
    """
    根据财富比率获取身份标签

    Args:
        wealth_ratio: 财富比率

    Returns:
        身份标签
    """
    if wealth_ratio > 5:
        return "县城土豪"
    elif wealth_ratio > 2:
        return "体面名流"
    elif wealth_ratio > 0.8:
        return "平替生活"
    else:
        return "生存挑战"

def generate_city_comparison(current_city: str, target_city: str, current_coli: float, target_coli: float) -> str:
    """
    生成城市对比描述

    Args:
        current_city: 当前城市
        target_city: 目标城市
        current_coli: 当前城市COLI指数
        target_coli: 目标城市COLI指数

    Returns:
        对比描述文本
    """
    import random

    comparisons = []

    ratio = current_coli / target_coli if target_coli > 0 else 1

    if ratio > 1.5:
        comparisons.append(f"你在{current_city}租一室户的钱，在{target_city}能住带院子的二层楼")
        comparisons.append(f"{current_city}的一碗面，够在{target_city}吃三顿")
        comparisons.append(f"{current_city}地铁月卡的价格，够在{target_city}打车满城跑一个月")

    elif ratio > 1:
        comparisons.append(f"你在{current_city}月薪过万，扣除房租所剩无几；在{target_city}同样收入能过得体面")
        comparisons.append(f"{current_city}的夜生活需要精打细算，{target_city}则可以随心所欲")
        comparisons.append(f"同样的工资，在{current_city}是月光族，在{target_city}是小康水平")

    elif ratio > 0.5:
        comparisons.append(f"虽然{target_city}收入略低，但生活质量反而更高")
        comparisons.append(f"在{current_city}舍不得打的，在{target_city}可以随时叫车")
        comparisons.append(f"{current_city}的水电费，够在{target_city}交双份还有余")

    else:
        comparisons.append(f"无论在{current_city}还是{target_city}，都得精打细算过日子")
        comparisons.append(f"两座城市的生活成本差距不大，关键看个人理财能力")
        comparisons.append(f"物价差不多，但{target_city}或许有更好的发展机会")

    return random.choice(comparisons)


@app.post("/api/v1/drift", response_model=DriftResponse)
async def calculate_drift(request: DriftRequest):
    """
    财富漂流计算接口

    Args:
        request: 财富漂流请求

    Returns:
        财富漂流结果
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Supabase 未初始化，真实漂流接口不可用")

        current_city_data = get_city_data(request.current_city)
        if not current_city_data:
            raise HTTPException(
                status_code=404,
                detail=f"城市 {request.current_city} 数据不存在"
            )

        target_city_data = get_city_data(request.target_city)
        if not target_city_data:
            raise HTTPException(
                status_code=404,
                detail=f"城市 {request.target_city} 数据不存在"
            )

        current_city_coli = current_city_data.get("coli_index", 0)
        target_city_coli = target_city_data.get("coli_index", 0)
        target_city_median_income = target_city_data.get("median_income", 0)

        if target_city_coli <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"城市 {request.target_city} 的 COLI 数据无效"
            )

        equivalent_amount = round(request.monthly_income * (current_city_coli / target_city_coli), 2)

        wealth_ratio = calculate_wealth_ratio(equivalent_amount, target_city_median_income)

        identity_label = get_identity_label(wealth_ratio)

        city_comparison = generate_city_comparison(
            request.current_city,
            request.target_city,
            current_city_coli,
            target_city_coli
        )

        ai_essay = ai_service.generate_drift_essay(
            request.current_city,
            request.target_city,
            request.monthly_income,
            equivalent_amount,
            identity_label
        )

        if not ai_essay:
            raise HTTPException(status_code=502, detail="AI 感言服务暂不可用")

        return {
            "current_city": request.current_city,
            "target_city": request.target_city,
            "current_city_coli": current_city_coli,
            "target_city_coli": target_city_coli,
            "equivalent_amount": equivalent_amount,
            "target_city_median_income": target_city_median_income,
            "wealth_ratio": wealth_ratio,
            "identity_label": identity_label,
            "city_comparison": city_comparison,
            "ai_essay": ai_essay
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"财富漂流计算失败: {str(e)}")
