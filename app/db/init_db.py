from app.db.database import SessionLocal, engine, Base
from app.models.models import Category, Product, Review, Cart, User, Promotion, PromotionUsage
from app.services.csv_importer import CSVImporterService
from app.db.create_admin import create_admin_user
import os


def init_database():
    """
    Инициализирует базу данных: создает таблицы и заполняет данными из CSV
    """
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    print("Таблицы базы данных созданы")

    # Создаем сессию базы данных
    db = SessionLocal()

    try:
        # Создаем администратора
        create_admin_user()

        # Проверяем, есть ли уже данные
        if not CSVImporterService.check_existing_data(db):
            # Импортируем данные из CSV
            csv_file_path = "tech_products.csv"
            CSVImporterService.import_from_csv(db, csv_file_path)
            print("База данных успешно инициализирована с данными из CSV")
        else:
            print("База данных уже содержит данные, пропускаем импорт")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    init_database()