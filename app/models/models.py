from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    reviews = relationship("Review", back_populates="user")
    cart_items = relationship("Cart", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Float, nullable=False)
    rating = Column(Float, default=0.0)

    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product")
    cart_items = relationship("Cart", back_populates="product")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    review_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    promo_code = Column(String, unique=True, index=True)
    discount_type = Column(String, nullable=False)  # 'percentage', 'fixed', 'free_shipping'
    discount_value = Column(Float)
    minimum_order_amount = Column(Float, default=0)
    maximum_discount = Column(Float)
    usage_limit = Column(Integer)
    used_count = Column(Integer, default=0)
    user_usage_limit = Column(Integer, default=1)

    # Даты активности
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Целевые категории/товары
    target_categories = Column(JSON)
    target_products = Column(JSON)
    excluded_products = Column(JSON)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    creator = relationship("User")
    usages = relationship("PromotionUsage", back_populates="promotion")


class PromotionUsage(Base):
    __tablename__ = "promotion_usage"

    id = Column(Integer, primary_key=True, index=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer)
    used_at = Column(DateTime(timezone=True), server_default=func.now())
    discount_amount = Column(Float, nullable=False)

    promotion = relationship("Promotion", back_populates="usages")
    user = relationship("User")