from app.db.database import SessionLocal
from app.services.auth import UserService, AuthService
from app.schemas.auth import UserCreate


def create_admin_user():
    db = SessionLocal()
    try:
        # Сильный пароль для администратора
        admin_data = UserCreate(
            email="admin@example.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            password="AdminSecurePass123!"
        )

        # Проверяем, существует ли уже администратор
        existing_admin = UserService.get_user_by_username(db, "admin")
        if existing_admin:
            print("Admin user already exists")
            return

        # Создаем администратора
        admin_user = UserService.create_user(db=db, user=admin_data)

        # Устанавливаем флаг суперпользователя
        admin_user.is_superuser = True
        db.commit()

        print("Admin user created successfully")
        print(f"Username: admin")
        print(f"Password: AdminSecurePass123!")
        print("Please change the password after first login!")

    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()