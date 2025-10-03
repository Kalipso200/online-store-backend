import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestPromotions:
    def test_create_promotion_as_admin(self, client, admin_headers):
        """Тест создания промо-акции администратором"""
        response = client.post(
            "/admin/",
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
        from datetime import datetime, timedelta

        # Используем реальные даты относительно текущего времени
        start_date = datetime.now() - timedelta(days=1)  # Началась вчера
        end_date = datetime.now() + timedelta(days=1)  # Закончится завтра

        # Сначала создаем промо-акцию
        promo_response = client.post(
            "/admin/",
            headers=admin_headers,
            json={
                "title": "Summer Sale",
                "promo_code": "SUMMER20",
                "discount_type": "percentage",
                "discount_value": 20.0,
                "minimum_order_amount": 0,  # Упростим для теста
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "is_active": True
            }
        )
        assert promo_response.status_code == status.HTTP_200_OK
        print(f"Promotion created: {promo_response.json()}")

        # Применяем промо-код
        response = client.post(
            "/promotions/apply",
            headers=admin_headers,
            json={
                "promo_code": "SUMMER20",
                "product_ids": [test_product.id],
                "total_amount": 100.0
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        print(f"Apply response: {data}")
        assert data["valid"] == True
        assert data["discount_amount"] == 20.0

    def test_promotion_usage_limit(self, client, db_session, admin_headers):
        """Тест ограничения использования промо-кода"""
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)

        # Создаем промо-акцию с лимитом 1 использование
        promo_response = client.post(
            "/admin/",
            headers=admin_headers,
            json={
                "title": "Limited Promotion",
                "promo_code": "LIMITED1",
                "discount_type": "fixed",
                "discount_value": 10.0,
                "usage_limit": 1,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "is_active": True
            }
        )
        assert promo_response.status_code == status.HTTP_200_OK
        promo_data = promo_response.json()
        promo_id = promo_data["id"]
        print(f"Created limited promotion: {promo_data}")

        # Применяем первый раз (должно работать)
        response1 = client.post(
            "/promotions/apply",
            headers=admin_headers,
            json={
                "promo_code": "LIMITED1",
                "product_ids": [],
                "total_amount": 100.0
            }
        )
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        print(f"First apply: {data1}")

        if data1["valid"]:
            # Если первый раз прошел, второй должен быть отклонен
            response2 = client.post(
                "/promotions/apply",
                headers=admin_headers,
                json={
                    "promo_code": "LIMITED1",
                    "product_ids": [],
                    "total_amount": 100.0
                }
            )
            assert response2.status_code == status.HTTP_200_OK
            data2 = response2.json()
            print(f"Second apply: {data2}")
            assert data2["valid"] == False
            assert "limit" in data2["message"].lower()
        else:
            print(f"First application failed: {data1['message']}")
            # Если первый раз не прошел, проверяем почему
            assert False, f"First application should be valid: {data1['message']}"

    def test_promotion_debug(self, client, db_session, admin_headers, test_product):
        """Диагностический тест промо-акций"""
        from datetime import datetime, timedelta

        print(f"=== PROMOTION DEBUG ===")
        print(f"Current time: {datetime.now()}")

        # Создаем промо-акцию с правильными датами
        start_date = datetime.now() - timedelta(days=1)  # Началась вчера
        end_date = datetime.now() + timedelta(days=1)  # Закончится завтра

        promo_response = client.post(
            "/admin/",
            headers=admin_headers,
            json={
                "title": "Debug Promotion",
                "promo_code": "DEBUG100",
                "discount_type": "percentage",
                "discount_value": 10.0,
                "minimum_order_amount": 0,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "is_active": True
            }
        )
        print(f"Create response: {promo_response.status_code}")
        if promo_response.status_code == 200:
            promo_data = promo_response.json()
            print(f"Created promotion: {promo_data}")

            # Проверим что промо-акция есть в базе
            from app.services.promotions import PromotionService
            db_promo = PromotionService.get_promotion_by_code(db_session, "DEBUG100")
            if db_promo:
                print(
                    f"DB promotion - start: {db_promo.start_date}, end: {db_promo.end_date}, active: {db_promo.is_active}")
                print(f"Now: {datetime.now()}")
                print(f"Is active now: {db_promo.start_date <= datetime.now() <= db_promo.end_date}")

        # Пробуем применить
        apply_response = client.post(
            "/promotions/apply",
            headers=admin_headers,
            json={
                "promo_code": "DEBUG100",
                "product_ids": [test_product.id],
                "total_amount": 100.0
            }
        )
        print(f"Apply response: {apply_response.status_code} - {apply_response.text}")
