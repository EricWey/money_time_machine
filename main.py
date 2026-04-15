from fastapi import FastAPI
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from supabase import create_client, Client

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


# 依赖项，用于获取 Supabase 客户端
def get_supabase():
    yield supabase

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
