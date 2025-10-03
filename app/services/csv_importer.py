import csv
import os
from sqlalchemy.orm import Session
from typing import List, Dict
from app.models.models import Product, Category
from app.schemas.items import ProductCreate, CategoryCreate


class CSVImporterService:
    @staticmethod
    def import_from_csv(db: Session, csv_file_path: str = "tech_products.csv"):
        """
        Импортирует данные из CSV файла в базу данных
        """
        if not os.path.exists(csv_file_path):
            print(f"CSV файл {csv_file_path} не найден")
            return
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            rows = list(csv_reader)

            # Создаем словарь для категорий
            categories_dict = {}
            products_to_create = []

            # Сначала собираем все уникальные категории
            for row in rows:
                category_id = int(row['id_категории'])
                category_name = row['категория'].strip()

                if category_id not in categories_dict:
                    categories_dict[category_id] = category_name
                    print(f"Найдена категория: {category_name} (ID: {category_id})")

            # Создаем категории в базе
            for category_id, category_name in categories_dict.items():
                # Проверяем, существует ли категория с таким ID
                existing_category = db.query(Category).filter(
                    Category.id == category_id
                ).first()

                if existing_category:
                    # Обновляем название категории если нужно
                    if existing_category.name != category_name:
                        existing_category.name = category_name
                        print(f"Обновлена категория: {category_name} (ID: {category_id})")
                    else:
                        print(f"Категория уже существует: {category_name} (ID: {category_id})")
                else:
                    # Создаем новую категорию
                    new_category = Category(
                        id=category_id,
                        name=category_name
                    )
                    db.add(new_category)
                    print(f"Создана категория: {category_name} (ID: {category_id})")

            db.commit()
            print(f"Создано/обновлено {len(categories_dict)} категорий")

            # Теперь обрабатываем товары
            products_created = 0
            products_updated = 0

            for row in rows:
                product_name = row['наименование'].strip()
                category_id = int(row['id_категории'])
                price = float(row['цена'])
                rating = float(row['рейтинг']) if row['рейтинг'] and row['рейтинг'].strip() else 0.0

                # Проверяем, существует ли продукт с таким названием
                existing_product = db.query(Product).filter(
                    Product.name == product_name
                ).first()

                if existing_product:
                    # Обновляем существующий товар
                    existing_product.category_id = category_id
                    existing_product.price = price
                    existing_product.rating = rating
                    products_updated += 1
                    print(f"Обновлен товар: {product_name}")
                else:
                    # Создаем новый товар
                    new_product = Product(
                        name=product_name,
                        category_id=category_id,
                        price=price,
                        rating=rating
                    )
                    db.add(new_product)
                    products_created += 1
                    print(f"Создан товар: {product_name} (категория ID: {category_id})")

            db.commit()
            print("=== ИМПОРТ ЗАВЕРШЕН ===")
            print(f"Создано товаров: {products_created}")
            print(f"Обновлено товаров: {products_updated}")
            print(f"Всего категорий: {len(categories_dict)}")

    @staticmethod
    def check_existing_data(db: Session) -> bool:
        """
        Проверяет, есть ли уже данные в базе
        """
        products_count = db.query(Product).count()
        categories_count = db.query(Category).count()

        print(f"Проверка данных: {products_count} товаров, {categories_count} категорий")
        return products_count > 0 or categories_count > 0

    @staticmethod
    def get_categories_info(db: Session) -> List[Dict]:
        """
        Возвращает информацию о категориях для отладки
        """
        categories = db.query(Category).all()
        result = []

        for cat in categories:
            products_count = db.query(Product).filter(Product.category_id == cat.id).count()
            result.append({
                "id": cat.id,
                "name": cat.name,
                "products_count": products_count,
                "products": [p.name for p in cat.products][:5]  # первые 5 товаров
            })

        return result

    @staticmethod
    def get_products_by_category(db: Session, category_id: int) -> List[Dict]:
        """
        Возвращает товары по категории для отладки
        """
        products = db.query(Product).filter(Product.category_id == category_id).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "category_id": p.category_id,
                "price": p.price,
                "rating": p.rating
            }
            for p in products
        ]