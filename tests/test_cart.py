import pytest
from fastapi import status


class TestCart:
    def test_add_to_cart_authenticated(self, client, auth_headers, test_product):
        """Тест добавления товара в корзину"""
        response = client.post(
            "/cart/",
            headers=auth_headers,
            json={
                "product_id": test_product.id,
                "quantity": 2
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["product_id"] == test_product.id
        assert data["quantity"] == 2

    def test_add_to_cart_unauthenticated(self, client, test_product):
        """Тест добавления в корзину без авторизации"""
        response = client.post(
            "/cart/",
            json={
                "product_id": test_product.id,
                "quantity": 1
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_cart(self, client, auth_headers, test_product):
        """Тест получения корзины"""
        # Сначала добавляем товар
        client.post(
            "/cart/",
            headers=auth_headers,
            json={
                "product_id": test_product.id,
                "quantity": 1
            }
        )

        response = client.get("/cart/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["product_id"] == test_product.id
        assert "total_price" in data[0]

    def test_update_cart_item(self, client, auth_headers, db_session, test_product, test_user):
        """Тест обновления товара в корзине"""
        from app.models.models import Cart
        # Создаем элемент корзины
        cart_item = Cart(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=1
        )
        db_session.add(cart_item)
        db_session.commit()

        response = client.put(
            f"/cart/{cart_item.id}",
            headers=auth_headers,
            json={"quantity": 3}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quantity"] == 3

    def test_clear_cart(self, client, auth_headers, db_session, test_product, test_user):
        """Тест очистки корзины"""
        from app.models.models import Cart
        # Добавляем товар в корзину
        cart_item = Cart(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=1
        )
        db_session.add(cart_item)
        db_session.commit()

        response = client.delete("/cart/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        # Проверяем, что корзина пуста
        response = client.get("/cart/", headers=auth_headers)
        data = response.json()
        assert len(data) == 0