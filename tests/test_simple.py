def test_simple_imports():
    """Простой тест импортов"""
    from app.db.database import Base, get_db
    from app.main import app
    from app.models.models import User
    from app.services.auth import AuthService

    assert Base is not None
    assert callable(get_db)
    assert app is not None
    assert User is not None
    assert AuthService is not None


def test_simple_db(db_session):
    """Простой тест БД"""
    from app.models.models import User
    from app.services.auth import AuthService

    # Создаем пользователя
    user = User(
        email="simple@example.com",
        username="simpleuser",
        first_name="Simple",
        last_name="User",
        hashed_password=AuthService.get_password_hash("sSimple123!9922222"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Проверяем что пользователь создался
    db_user = db_session.query(User).filter(User.username == "simpleuser").first()
    assert db_user is not None
    assert db_user.email == "simple@example.com"


def test_simple_auth_with_direct_token(client, db_session):
    """Тест аутентификации с прямым созданием токена"""
    from app.models.models import User
    from app.services.auth import AuthService

    # Сначала удаляем существующего пользователя если есть
    existing_user = db_session.query(User).filter(User.email == "token@example.com").first()
    if existing_user:
        db_session.delete(existing_user)
        db_session.commit()

    # Создаем пользователя
    user = User(
        email="token@example.com",
        username="tokenuser",
        first_name="Token",
        last_name="User",
        hashed_password=AuthService.get_password_hash("token123!eeeeDDDDCC"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    print(f"🔍 Created user ID: {user.id}, username: {user.username}")

    # Создаем токен напрямую - убедитесь что используем правильный ID
    token = AuthService.create_access_token(data={"sub": str(user.id)})
    print(f"🔍 Created token for user ID: {user.id}")

    # Используем токен
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)

    print(f"🔍 Response status: {response.status_code}")
    print(f"🔍 Response text: {response.text}")

    if response.status_code == 200:
        data = response.json()
        print(f"🔍 Returned user data - username: '{data.get('username')}', email: '{data.get('email')}'")
        print(f"🔍 Returned user ID: {data.get('id')}")

        # Проверяем что вернулся правильный пользователь
        assert data["username"] == "tokenuser"
        assert data["email"] == "token@example.com"
    else:
        # Если ошибка, выводим детали
        print(f"❌ Error response: {response.json()}")
        assert False, f"Expected 200, got {response.status_code}"