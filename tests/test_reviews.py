import pytest
from fastapi import status


class TestReviews:
    def test_create_review_authenticated(self, client, auth_headers, test_product):
        """Тест создания отзыва авторизованным пользователем"""
        response = client.post(
            "/reviews/",
            headers=auth_headers,
            json={
                "product_id": test_product.id,
                "review_text": "Great product!"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["review_text"] == "Great product!"
        assert data["product_id"] == test_product.id

    def test_create_review_unauthenticated(self, client, test_product):
        """Тест создания отзыва без авторизации"""
        response = client.post(
            "/reviews/",
            json={
                "product_id": test_product.id,
                "review_text": "Great product!"
            }
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_get_product_reviews(self, client, db_session, test_product, test_user):
        """Тест получения отзывов товара"""
        from app.models.models import Review

        # Очищаем старые отзывы для этого продукта
        db_session.query(Review).filter(Review.product_id == test_product.id).delete()
        db_session.commit()

        # Создаем тестовый отзыв
        review = Review(
            user_id=test_user.id,
            product_id=test_product.id,
            review_text="Test review"
        )
        db_session.add(review)
        db_session.commit()

        response = client.get(f"/reviews/product/{test_product.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["review_text"] == "Test review"

    def test_update_own_review(self, client, auth_headers, db_session, test_product, test_user):
        """Тест обновления собственного отзыва"""
        from app.models.models import Review

        # Очищаем старые отзывы
        db_session.query(Review).filter(Review.product_id == test_product.id).delete()
        db_session.commit()

        # Создаем отзыв
        review = Review(
            user_id=test_user.id,
            product_id=test_product.id,
            review_text="Original review"
        )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)

        response = client.put(
            f"/reviews/{review.id}",
            headers=auth_headers,
            json={"review_text": "Updated review"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["review_text"] == "Updated review"

    def test_delete_own_review(self, client, auth_headers, db_session, test_product, test_user):
        """Тест удаления собственного отзыва"""
        from app.models.models import Review

        # Очищаем старые отзывы
        db_session.query(Review).filter(Review.product_id == test_product.id).delete()
        db_session.commit()

        # Создаем отзыв
        review = Review(
            user_id=test_user.id,
            product_id=test_product.id,
            review_text="Review to delete"
        )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)

        response = client.delete(
            f"/reviews/{review.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

        # Проверяем, что отзыв удален
        remaining_reviews = db_session.query(Review).filter(Review.product_id == test_product.id).all()
        assert len(remaining_reviews) == 0