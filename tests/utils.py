import json
from typing import Dict, Any

def assert_response_structure(response, expected_status: int = 200):
    """Проверяет базовую структуру ответа"""
    assert response.status_code == expected_status
    if expected_status == 200:
        assert "message" in response.json() or "id" in response.json()

def create_test_promotion_data() -> Dict[str, Any]:
    """Создает тестовые данные для промо-акции"""
    return {
        "title": "Test Promotion",
        "description": "Test description",
        "promo_code": "TEST2024",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "minimum_order_amount": 100.0,
        "maximum_discount": 50.0,
        "usage_limit": 100,
        "user_usage_limit": 1,
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-12-31T23:59:59",
        "is_active": True
    }