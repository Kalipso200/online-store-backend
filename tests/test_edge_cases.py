import pytest
from fastapi import status
from datetime import datetime, timedelta

class TestEdgeCases:
    def test_large_pagination(self, client, db_session, test_category):
        """Тест пагинации с большими значениями"""
        response = client.get("/products/?skip=1000000&limit=1000000")
        assert response.status_code == status.HTTP_200_OK
        # Должен вернуть пустой список, а не ошибку

    def test_negative_pagination(self, client):
        """Тест пагинации с отрицательными значениями"""
        response = client.get("/products/?skip=-1&limit=-1")
        assert response.status_code == status.HTTP_200_OK

    def test_special_characters_in_search(self, client):
        """Тест специальных символов в параметрах"""
        response = client.get("/products/?category_id=1'; DROP TABLE products; --")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_very_long_password(self, client):
        """Тест очень длинного пароля"""
        long_password = "A" * 1000
        response = client.post(
            "/auth/register",
            json={
                "email": "longpass@example.com",
                "username": "longpassuser",
                "first_name": "Long",
                "last_name": "Password",
                "password": long_password
            }
        )
        # Должен либо принять, либо вернуть понятную ошибку
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_promotion_boundary_dates(self, client, admin_headers):
        """Тест граничных дат для промо-акций"""
        # Акция, которая начинается и заканчивается в одну и ту же дату
        response = client.post(
            "/promotions/",
            headers=admin_headers,
            json={
                "title": "Boundary Date Test",
                "promo_code": "BOUNDARY",
                "discount_type": "percentage",
                "discount_value": 10.0,
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-01-01T00:00:00",  # Та же дата
                "is_active": True
            }
        )
        # Должен вернуть ошибку валидации
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_very_high_discount(self, client, admin_headers):
        """Тест очень высокой скидки"""
        response = client.post(
            "/promotions/",
            headers=admin_headers,
            json={
                "title": "High Discount",
                "promo_code": "HIGH100",
                "discount_type": "percentage",
                "discount_value": 1000.0,  # 1000% скидка
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "is_active": True
            }
        )
        # Должен вернуть ошибку валидации
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY