from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class MacroEconomics(Base):
    """宏观经济数据模型 - 对应 TRD 2.1"""
    __tablename__ = 'macro_economics'

    year = Column(Integer, primary_key=True)
    cpi_index = Column(DECIMAL(18, 4), nullable=False)
    m2_growth = Column(DECIMAL(18, 4), nullable=False)
    gdp_growth = Column(DECIMAL(18, 4), nullable=False)
    m2_adj = Column(DECIMAL(18, 4), nullable=False) # M2增速 - GDP增速
    property_index_nat = Column(DECIMAL(18, 4))     # 全国房价基准
    updated_at = Column(DateTime, server_default=func.now())

class CityData(Base):
    """城市索引模型 - 对应 TRD 2.2"""
    __tablename__ = 'city_data'

    city_id = Column(Integer, primary_key=True)
    city_name = Column(String(50), nullable=False)
    province = Column(String(50), nullable=False)
    coli_index = Column(DECIMAL(18, 2), nullable=False, default=100.00)
    median_income = Column(DECIMAL(18, 2))
    region_level = Column(Integer, default=2) # 1-省会, 2-地级市
    updated_at = Column(DateTime, server_default=func.now())

class CityPrice(Base):
    """实物购买力矩阵模型 - 供 RAG 和 转换器 使用"""
    __tablename__ = 'city_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('city_data.city_id'))
    year = Column(Integer, nullable=False)
    category = Column(String(20)) # food, housing, trans, service
    item_name = Column(String(50))
    price = Column(DECIMAL(18, 2))
    unit = Column(String(10))
    is_essential = Column(Boolean, default=True)
