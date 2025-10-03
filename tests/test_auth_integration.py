import pytest
from fastapi import status


def test_full_auth_flow(client, db_session):
    """Полный тест потока аутентификации"""

    # 1. Регистрация с простым паролем
    register_response = client.post(
        "/auth/register",
        json={
            "email": "flow@example.com",
            "username": "flowuser",
            "first_name": "Flow",
            "last_name": "User",
            "password": "flow123"  # Простой пароль
        }
    )

    print(f"Register: {register_response.status_code} - {register_response.text}")
    assert register_response.status_code == 200

    # 2. Логин
    login_response = client.post(
        "/auth/login",
        json={
            "username": "flowuser",
            "password": "flow123"
        }
    )

    print(f"Login: {login_response.status_code} - {login_response.text}")
    assert login_response.status_code == 200

    login_data = login_response.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    assert login_data["token_type"] == "bearer"

    # 3. Использование токена
    headers = {"Authorization": f"Bearer {login_data['access_token']}"}
    me_response = client.get("/auth/me", headers=headers)

    print(f"Me: {me_response.status_code} - {me_response.text}")
    assert me_response.status_code == 200

    me_data = me_response.json()
    assert me_data["username"] == "flowuser"
    assert me_data["email"] == "flow@example.com"