#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财富漂流瓶功能单元测试
"""

import pytest
from fastapi.testclient import TestClient
from main import app, calculate_wealth_ratio, get_identity_label, generate_city_comparison

client = TestClient(app)

class TestWealthRatioCalculation:
    """测试财富比率计算"""

    def test_normal_case(self):
        """正常情况"""
        assert calculate_wealth_ratio(10000, 2000) == 5.0
        assert calculate_wealth_ratio(5000, 2500) == 2.0

    def test_zero_median_income(self):
        """中位数收入为零"""
        assert calculate_wealth_ratio(10000, 0) == 0.0

    def test_negative_median_income(self):
        """中位数收入为负数"""
        assert calculate_wealth_ratio(10000, -100) == 0.0

    def test_large_ratio(self):
        """大比率"""
        result = calculate_wealth_ratio(50000, 1000)
        assert result == 50.0
        assert result > 5

    def test_small_ratio(self):
        """小比率"""
        result = calculate_wealth_ratio(1000, 5000)
        assert result == 0.2
        assert result < 0.8


class TestIdentityLabel:
    """测试身份标签判定"""

    def test_county_tyrant(self):
        """县城土豪"""
        assert get_identity_label(6.0) == "县城土豪"
        assert get_identity_label(10.5) == "县城土豪"
        assert get_identity_label(100.0) == "县城土豪"

    def test_decent_celebrity(self):
        """体面名流"""
        assert get_identity_label(3.0) == "体面名流"
        assert get_identity_label(4.5) == "体面名流"
        assert get_identity_label(2.01) == "体面名流"

    def test_substitute_life(self):
        """平替生活"""
        assert get_identity_label(1.5) == "平替生活"
        assert get_identity_label(1.0) == "平替生活"
        assert get_identity_label(0.81) == "平替生活"

    def test_survival_challenge(self):
        """生存挑战"""
        assert get_identity_label(0.5) == "生存挑战"
        assert get_identity_label(0.79) == "生存挑战"
        assert get_identity_label(0.1) == "生存挑战"
        assert get_identity_label(0.0) == "生存挑战"


class TestCityComparison:
    """测试城市对比描述生成"""

    def test_high_ratio_comparison(self):
        """高比值场景"""
        comparison = generate_city_comparison("上海", "开封", 100, 52)
        assert "上海" in comparison
        assert "开封" in comparison
        assert len(comparison) > 0

    def test_medium_ratio_comparison(self):
        """中等比值场景"""
        comparison = generate_city_comparison("北京", "郑州", 98, 65)
        assert "北京" in comparison
        assert "郑州" in comparison
        assert len(comparison) > 0

    def test_low_ratio_comparison(self):
        """低比值场景"""
        comparison = generate_city_comparison("郑州", "鹤岗", 65, 30)
        assert "郑州" in comparison
        assert "鹤岗" in comparison
        assert len(comparison) > 0

    def test_zero_target_coli(self):
        """目标城市COLI为零"""
        comparison = generate_city_comparison("上海", "某城", 100, 0)
        assert len(comparison) > 0


class TestDriftAPI:
    """测试财富漂流API接口"""

    def test_health_check(self):
        """健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_same_city_error(self):
        """相同城市错误"""
        response = client.post("/api/v1/drift", json={
            "current_city": "上海",
            "monthly_income": 10000,
            "target_city": "上海"
        })
        assert response.status_code == 422
        assert "当前城市和目标城市不能相同" in response.json()["detail"][0]["msg"]

    def test_city_not_found(self):
        """城市数据不存在"""
        response = client.post("/api/v1/drift", json={
            "current_city": "长沙",
            "monthly_income": 10000,
            "target_city": "开封"
        })
        assert response.status_code == 404
        assert "数据不存在" in response.json()["detail"]

    def test_negative_income_error(self):
        """负收入错误"""
        response = client.post("/api/v1/drift", json={
            "current_city": "上海",
            "monthly_income": -5000,
            "target_city": "开封"
        })
        assert response.status_code == 422

    def test_zero_income_error(self):
        """零收入错误"""
        response = client.post("/api/v1/drift", json={
            "current_city": "上海",
            "monthly_income": 0,
            "target_city": "开封"
        })
        assert response.status_code == 422

    def test_missing_fields(self):
        """缺少必填字段"""
        response = client.post("/api/v1/drift", json={
            "current_city": "上海"
        })
        assert response.status_code == 422


class TestConvertAPI:
    """测试货币购买力转换API接口"""

    def test_normal_conversion(self):
        """正常转换"""
        response = client.post("/api/v1/convert", json={
            "amount": 100,
            "source_year": 1990,
            "city": "北京"
        })
        assert response.status_code == 200
        data = response.json()
        assert "equivalent_amount" in data
        assert "items" in data
        assert "ai_comment" in data
        assert data["equivalent_amount"] > 0
        assert len(data["items"]) == 3
        for item in data["items"]:
            assert item["unit"]
            assert item["note"]
            assert item["category"]

    def test_invalid_year_too_old(self):
        """年份太旧"""
        response = client.post("/api/v1/convert", json={
            "amount": 100,
            "source_year": 1970,
            "city": "北京"
        })
        assert response.status_code == 422

    def test_invalid_city(self):
        """无效城市"""
        response = client.post("/api/v1/convert", json={
            "amount": 100,
            "source_year": 1990,
            "city": "长沙"
        })
        assert response.status_code == 422
        assert "无效" in response.json()["detail"][0]["msg"]

    def test_negative_amount(self):
        """负数金额"""
        response = client.post("/api/v1/convert", json={
            "amount": -100,
            "source_year": 1990,
            "city": "北京"
        })
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
