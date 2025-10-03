from app.db.database import SessionLocal
from app.services.auth import UserService, AuthService
from app.schemas.auth import UserCreate


def create_admin_user():
    db = SessionLocal()
    try:
        # Проверяем, существует ли уже администратор
        existing_admin = UserService.get_user_by_username(db, "admin")
        if existing_admin:
            print(f" Admin user already exists (ID: {existing_admin.id})")
            return existing_admin

        # Создаем администратора
        admin_data = UserCreate(
            email="admin@example.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            password="AdminSecurePass123!"
        )

        admin_user = UserService.create_user(db=db, user=admin_data)
        admin_user.is_superuser = True
        db.commit()

        print(f" Admin user created successfully (ID: {admin_user.id})")
        return admin_user

    except Exception as e:
        print(f" Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
