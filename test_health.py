from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """测试健康检查接口"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "app_version" in data
    assert "database_status" in data
    assert data["database_status"] == "connected"

def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "欢迎使用钱值时光机API"
    assert "version" in data
    assert data["docs"] == "/docs"
