import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Добавляем корневую директорию в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.database import Base, get_db

# Используем SQLite для тестов
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Создаем таблицы
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session  # Используем ту же сессию!
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# Упрощенные фикстуры для пользователей
@pytest.fixture
def test_user(db_session):
    """Создает тестового пользователя"""
    from app.models.models import User
    from app.services.auth import AuthService

    # Удаляем существующего пользователя если есть
    db_session.query(User).filter(User.username == "testuser").delete()
    db_session.commit()

    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password=AuthService.get_password_hash("test123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(client, test_user):
    """Получает токен для тестового пользователя"""
    # Используем прямое создание токена чтобы избежать проблем с логином
    from app.services.auth import AuthService
    return AuthService.create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}