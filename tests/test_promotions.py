import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestPromotions:
    def test_create_promotion_as_admin(self, client, admin_headers):
        """Тест создания промо-акции администратором"""
        response = client.post(
            "/promotions/",
            headers=admin_headers,
            json={
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
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["promo_code"] == "TEST2024"
        assert data["discount_value"] == 10.0

    def test_apply_valid_promotion(self, client, db_session, admin_headers, test_product):
        """Тест применения валидного промо-кода"""
        # Сначала создаем промо-акцию
        promo_response = client.post(
            "/promotions/",
            headers=admin_headers,
            json={
                "title": "Summer Sale",
                "promo_code": "SUMMER20",
                "discount_type": "percentage",
                "discount_value": 20.0,
                "minimum_order_amount": 50.0,
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "is_active": True
            }
        )

        # Применяем промо-код
        response = client.post(
            "/promotions/apply",
            headers={"Authorization": f"Bearer {admin_headers['Authorization'].split(' ')[1]}"},
            json={
                "promo_code": "SUMMER20",
                "product_ids": [test_product.id],
                "total_amount": 100.0
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] == True
        assert data["discount_amount"] == 20.0
        assert data["final_amount"] == 80.0

    def test_apply_expired_promotion(self, client, admin_headers):
        """Тест применения просроченной промо-акции"""
        response = client.post(
            "/promotions/",
            headers=admin_headers,
            json={
                "title": "Expired Promotion",
                "promo_code": "EXPIRED",
                "discount_type": "percentage",
                "discount_value": 10.0,
                "start_date": "2023-01-01T00:00:00",
                "end_date": "2023-12-31T23:59:59",  # Прошлый год
                "is_active": True
            }
        )

        apply_response = client.post(
            "/promotions/apply",
            headers={"Authorization": f"Bearer {admin_headers['Authorization'].split(' ')[1]}"},
            json={
                "promo_code": "EXPIRED",
                "product_ids": [],
                "total_amount": 100.0
            }
        )
        assert apply_response.status_code == status.HTTP_200_OK
        data = apply_response.json()
        assert data["valid"] == False
        assert "expired" in data["message"].lower()

    def test_promotion_usage_limit(self, client, db_session, admin_headers):
        """Тест ограничения использования промо-кода"""
        # Создаем промо-акцию с лимитом 1 использование
        promo_response = client.post(
            "/promotions/",
            headers=admin_headers,
            json={
                "title": "Limited Promotion",
                "promo_code": "LIMITED1",
                "discount_type": "fixed",
                "discount_value": 10.0,
                "usage_limit": 1,
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "is_active": True
            }
        )
        promo_id = promo_response.json()["id"]

        # Записываем использование
        from app.services.promotions import PromotionService
        PromotionService.record_promotion_usage(
            db=db_session,
            promotion_id=promo_id,
            user_id=1,
            discount_amount=10.0
        )

        # Пытаемся применить снова
        response = client.post(
            "/promotions/apply",
            headers={"Authorization": f"Bearer {admin_headers['Authorization'].split(' ')[1]}"},
            json={
                "promo_code": "LIMITED1",
                "product_ids": [],
                "total_amount": 100.0
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] == False
        assert "limit" in data["message"].lower()