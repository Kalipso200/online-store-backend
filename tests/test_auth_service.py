def test_auth_service_directly(db_session):
    """Тестируем сервис аутентификации напрямую"""
    from app.services.auth import UserService, AuthService
    from app.schemas.auth import UserCreate
    from app.models.models import User

    # 1. Создаем пользователя через сервис
    user_data = UserCreate(
        email="service@example.com",
        username="serviceuser",
        first_name="Service",
        last_name="User",
        password="service123"
    )

    user = UserService.create_user(db=db_session, user=user_data)
    assert user.id is not None
    assert user.email == "service@example.com"

    # 2. Аутентифицируем пользователя
    auth_user = UserService.authenticate_user(db=db_session, username="serviceuser", password="service123")
    assert auth_user is not None
    assert auth_user.id == user.id

    # 3. Проверяем неверный пароль
    wrong_auth = UserService.authenticate_user(db=db_session, username="serviceuser", password="wrongpassword")
    assert wrong_auth is None

    # 4. Проверяем создание токена
    token = AuthService.create_access_token(data={"sub": str(user.id)})
    assert token is not None

    # 5. Проверяем верификацию токена
    payload = AuthService.verify_token(token)
    assert payload is not None
    assert payload["sub"] == str(user.id)