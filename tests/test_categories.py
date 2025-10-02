import pytest
from fastapi import status


class TestCategories:
    def test_get_categories_empty(self, client):
        """Тест получения пустого списка категорий"""
        response = client.get("/categories/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_category_as_admin(self, client, admin_headers):
        """Тест создания категории администратором"""
        response = client.post(
            "/categories/",
            headers=admin_headers,
            json={"name": "New Category"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Category"
        assert "id" in data

    def test_create_duplicate_category(self, client, admin_headers, test_category):
        """Тест создания дубликата категории"""
        response = client.post(
            "/categories/",
            headers=admin_headers,
            json={"name": "Test Category"}  # Существующее имя
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_category_by_id(self, client, test_category):
        """Тест получения категории по ID"""
        response = client.get(f"/categories/{test_category.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Category"

    def test_delete_category_as_admin(self, client, admin_headers, test_category):
        """Тест удаления категории администратором"""
        response = client.delete(
            f"/categories/{test_category.id}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK

        # Проверяем, что категория удалена
        response = client.get(f"/categories/{test_category.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND