import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем корневую директорию в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.database import Base, get_db

TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://test_user:test_password@test-db:5432/test_db")


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(TEST_DATABASE_URL)

    # Создаем таблицы
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Для тестов можно дропать таблицы, но осторожно
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Создает тестового пользователя"""
    from app.models.models import User
    from app.services.auth import AuthService

    # Очищаем всех пользователей
    db_session.query(User).delete()
    db_session.commit()

    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password=AuthService.get_password_hash("TestPassword123!"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user):
    """Получает токен для тестового пользователя"""
    from app.services.auth import AuthService
    return AuthService.create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def test_category(db_session):
    """Создает тестовую категорию"""
    from app.models.models import Category

    # Используем существующую категорию или создаем новую
    existing_category = db_session.query(Category).first()
    if existing_category:
        return existing_category

    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_product(db_session, test_category):
    """Создает тестовый продукт """
    from app.models.models import Product

    # Используем существующий продукт или создаем новый
    existing_product = db_session.query(Product).first()
    if existing_product:
        return existing_product

    product = Product(
        name="Test Product",
        price=99.99,
        category_id=test_category.id,
        rating=5
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def admin_user(db_session):
    """Создает администратора"""
    from app.models.models import User
    from app.services.auth import AuthService

    admin = User(
        email="admin@test.com",
        username="adminuser",
        first_name="Admin",
        last_name="User",
        hashed_password=AuthService.get_password_hash("AdminPass123!!!"),
        is_active=True,
        is_superuser=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def admin_token(admin_user):
    """Получает токен для администратора"""
    from app.services.auth import AuthService
    return AuthService.create_access_token(data={"sub": str(admin_user.id)})


@pytest.fixture
def admin_headers(admin_token):
    """Создает заголовки авторизации для администратора"""

    return {"Authorization": f"Bearer {admin_token}"}
