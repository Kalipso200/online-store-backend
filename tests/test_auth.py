import pytest
from fastapi import status


class TestAuth:
    def test_register_success(self, client):
        """Тест успешной регистрации"""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "password": "NewPassword123!"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "password" not in data

    def test_register_duplicate_email(self, client, test_user):
        """Тест регистрации с существующим email"""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",  # Существующий email
                "username": "differentuser",
                "first_name": "Different",
                "last_name": "User",
                "password": "Password123!"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password(self, client):
        """Тест регистрации со слабым паролем"""
        response = client.post(
            "/auth/register",
            json={
                "email": "weak@example.com",
                "username": "weakuser",
                "first_name": "Weak",
                "last_name": "User",
                "password": "123"  # Слишком короткий пароль
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client, test_user):
        """Тест успешного входа"""
        response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "TestPassword123!"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Тест входа с неправильным паролем"""
        response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Тест входа несуществующего пользователя"""
        response = client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": "Password123!"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, client, user_token):
        """Тест обновления токена"""
        # Сначала получаем refresh token через логин
        login_response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "TestPassword123!"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_change_password(self, client, auth_headers):
        """Тест смены пароля"""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "TestPassword123!",
                "new_password": "NewPassword123!"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Password changed successfully"

    def test_change_password_wrong_current(self, client, auth_headers):
        """Тест смены пароля с неправильным текущим паролем"""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword123!"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_current_user(self, client, auth_headers):
        """Тест получения информации о текущем пользователе"""
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_get_current_user_unauthorized(self, client):
        """Тест получения информации о пользователе без авторизации"""
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN