from fastapi.testclient import TestClient
import main

from main import app

client = TestClient(app)


class _SupabaseHealthStub:
    def table(self, _name):
        return self

    def select(self, _fields):
        return self

    def limit(self, _count):
        return self

    def execute(self):
        return type("Result", (), {"data": [{"year": 2024}]})()


def test_health_check(monkeypatch):
    """测试健康检查接口"""
    monkeypatch.setattr(main, "supabase", _SupabaseHealthStub())
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
