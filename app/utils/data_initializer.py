import csv
import logging
from sqlalchemy.orm import Session
from app.models.models import Category, Product
from app.core.security import get_password_hash
from app.models.models import User

logger = logging.getLogger(__name__)


def initialize_database_from_csv(db: Session, csv_file_path: str = "sample_products.csv"):
    """Инициализация базы данных из CSV файла"""
    logger.info(f"📁 Загрузка данных из CSV файла: {csv_file_path}")

    try:
        # Создаем тестового пользователя если нет
        if db.query(User).count() == 0:
            logger.info("👤 Создаем тестовых пользователей...")
            admin_user = User(
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True
            )
            db.add(admin_user)

            test_user = User(
                email="user@example.com",
                first_name="Test",
                last_name="User",
                hashed_password=get_password_hash("user123")
            )
            db.add(test_user)
            db.commit()
            logger.info("✅ Тестовые пользователи созданы")

        # Загружаем данные из CSV
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            products_created = 0
            categories_created = 0

            for row in csv_reader:
                # Создаем/получаем категорию
                category_name = row.get('category', 'Разное')
                category = db.query(Category).filter(Category.name == category_name).first()

                if not category:
                    category = Category(name=category_name, description=f"Товары категории {category_name}")
                    db.add(category)
                    categories_created += 1
                    logger.debug(f"➕ Создана категория: {category_name}")

                # Создаем товар
                product = Product(
                    name=row['name'],
                    description=row.get('description', ''),
                    price=float(row['price']),
                    stock_quantity=int(row.get('stock_quantity', 10)),
                    image_url=row.get('image_url', '')
                )
                product.categories.append(category)
                db.add(product)
                products_created += 1
                logger.debug(f"➕ Создан товар: {row['name']}")

            db.commit()
            logger.info(f"✅ Загружено {products_created} товаров и создано {categories_created} категорий из CSV")

    except FileNotFoundError:
        logger.warning(f"⚠️ CSV файл {csv_file_path} не найден. Продолжаем с пустой БД.")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Ошибка при загрузке данных из CSV: {e}")
        raise