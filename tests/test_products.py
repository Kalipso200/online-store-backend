import pytest
from fastapi import status


class TestProducts:
    def test_get_products_empty(self, client):
        """Тест получения пустого списка товаров"""
        response = client.get("/products/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_product_as_admin(self, client, admin_headers, test_category):
        """Тест создания товара администратором"""
        response = client.post(
            "/products/",
            headers=admin_headers,
            json={
                "name": "New Product",
                "category_id": test_category.id,
                "price": 99.99,
                "rating": 4.5
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Product"
        assert data["price"] == 99.99
        assert "id" in data

    def test_create_product_as_user(self, client, auth_headers, test_category):
        """Тест создания товара обычным пользователем (должен быть запрещен)"""
        response = client.post(
            "/products/",
            headers=auth_headers,
            json={
                "name": "New Product",
                "category_id": test_category.id,
                "price": 99.99,
                "rating": 4.5
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_products_with_filters(self, client, test_product):
        """Тест получения товаров с фильтрами"""
        # Фильтр по категории
        response = client.get(f"/products/?category_id={test_product.category_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Product"

        # Фильтр по цене
        response = client.get("/products/?min_price=50&max_price=150")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1

        # Фильтр по рейтингу
        response = client.get("/products/?min_rating=4.0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1

    def test_get_product_by_id(self, client, test_product):
        """Тест получения товара по ID"""
        response = client.get(f"/products/{test_product.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["category_name"] == "Test Category"

    def test_get_nonexistent_product(self, client):
        """Тест получения несуществующего товара"""
        response = client.get("/products/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_product_as_admin(self, client, admin_headers, test_product):
        """Тест обновления товара администратором"""
        response = client.put(
            f"/products/{test_product.id}",
            headers=admin_headers,
            json={
                "name": "Updated Product",
                "price": 149.99
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["price"] == 149.99

    def test_delete_product_as_admin(self, client, admin_headers, test_product):
        """Тест удаления товара администратором"""
        response = client.delete(
            f"/products/{test_product.id}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK

        # Проверяем, что товар действительно удален
        response = client.get(f"/products/{test_product.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_pagination(self, client, db_session, test_category):
        """Тест пагинации товаров"""
        # Создаем несколько товаров
        from app.models.models import Product
        for i in range(15):
            product = Product(
                name=f"Product {i}",
                category_id=test_category.id,
                price=100 + i,
                rating=4.0
            )
            db_session.add(product)
        db_session.commit()

        # Тестируем пагинацию
        response = client.get("/products/?skip=5&limit=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5