from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from models import Base, MacroEconomics, CityData, CityPrice

class Settings(BaseSettings):
    """应用配置"""
    APP_NAME: str = "钱值时光机"
    APP_VERSION: str = "v1.0.0"
    DATABASE_URL: str = "sqlite:///./money_time_machine.db"
    model_config = ConfigDict(env_file=".env")

settings = Settings()

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 依赖项，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
        # 测试数据库连接
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
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
