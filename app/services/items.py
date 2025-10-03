from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.models import Product, Category, Review, Cart
from app.schemas.items import (
    ProductCreate, ProductUpdate, CategoryCreate,
    ReviewCreate, ReviewUpdate, CartCreate, CartUpdate
)


class ProductService:
    @staticmethod
    def get_products(
            db: Session,
            skip: int = 0,
            limit: int = 100,
            category_id: Optional[int] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            min_rating: Optional[float] = None
    ) -> List[Product]:
        query = db.query(Product)

        if category_id:
            query = query.filter(Product.category_id == category_id)
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        if min_rating is not None:
            query = query.filter(Product.rating >= min_rating)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_product(db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def create_product(db: Session, product: ProductCreate) -> Product:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product:
            update_data = product_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_product, field, value)
            db.commit()
            db.refresh(db_product)
        return db_product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product:
            db.delete(db_product)
            db.commit()
            return True
        return False


class CategoryService:
    @staticmethod
    def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
        return db.query(Category).offset(skip).limit(limit).all()

    @staticmethod
    def get_category(db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def create_category(db: Session, category: CategoryCreate) -> Category:
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if db_category:
            db.delete(db_category)
            db.commit()
            return True
        return False


class ReviewService:
    @staticmethod
    def get_review_by_id(db: Session, review_id: int) -> Optional[Review]:
        return db.query(Review).filter(Review.id == review_id).first()

    @staticmethod
    def get_reviews_by_product(db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return db.query(Review).filter(
            Review.product_id == product_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_reviews_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return db.query(Review).filter(
            Review.user_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def create_review(db: Session, review_data: dict) -> Review:
        db_review = Review(**review_data)
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return db_review

    @staticmethod
    def update_review(db: Session, review_id: int, review_update: ReviewUpdate) -> Optional[Review]:
        db_review = db.query(Review).filter(Review.id == review_id).first()
        if db_review:
            update_data = review_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_review, field, value)
            db.commit()
            db.refresh(db_review)
        return db_review

    @staticmethod
    def delete_review(db: Session, review_id: int) -> bool:
        db_review = db.query(Review).filter(Review.id == review_id).first()
        if db_review:
            db.delete(db_review)
            db.commit()
            return True
        return False


class CartService:
    @staticmethod
    def get_cart_item_by_id(db: Session, cart_id: int) -> Optional[Cart]:
        return db.query(Cart).filter(Cart.id == cart_id).first()

    @staticmethod
    def get_user_cart(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Cart]:
        return db.query(Cart).filter(
            Cart.user_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_cart_item(db: Session, user_id: int, product_id: int) -> Optional[Cart]:
        return db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        ).first()

    @staticmethod
    def add_to_cart(db: Session, cart_data: dict) -> Cart:
        user_id = cart_data['user_id']
        product_id = cart_data['product_id']
        quantity = cart_data.get('quantity', 1)

        # Проверяем, есть ли уже товар в корзине
        existing_item = CartService.get_cart_item(db, user_id, product_id)

        if existing_item:
            # Обновляем количество
            existing_item.quantity += quantity
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            # Создаем новую запись
            db_cart = Cart(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(db_cart)
            db.commit()
            db.refresh(db_cart)
            return db_cart

    @staticmethod
    def update_cart_item(db: Session, cart_id: int, cart_update: CartUpdate) -> Optional[Cart]:
        db_cart = CartService.get_cart_item_by_id(db, cart_id)
        if db_cart:
            update_data = cart_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_cart, field, value)
            db.commit()
            db.refresh(db_cart)
        return db_cart

    @staticmethod
    def remove_from_cart(db: Session, cart_id: int) -> bool:
        db_cart = CartService.get_cart_item_by_id(db, cart_id)
        if db_cart:
            db.delete(db_cart)
            db.commit()
            return True
        return False

    @staticmethod
    def clear_user_cart(db: Session, user_id: int) -> bool:
        db.query(Cart).filter(Cart.user_id == user_id).delete()
        db.commit()
        return True