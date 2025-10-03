from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


# Category Schemas
class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Product Schemas
class ProductBase(BaseModel):
    name: str
    category_id: int
    price: float
    rating: Optional[float] = 0.0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    rating: Optional[float] = None


class Product(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductWithCategory(Product):
    category_name: Optional[str] = None


# Review Schemas
class ReviewBase(BaseModel):
    product_id: int
    review_text: str


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    review_text: Optional[str] = None


class Review(ReviewBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewWithUser(Review):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# Cart Schemas
class CartBase(BaseModel):
    product_id: int
    quantity: int = 1


class CartCreate(CartBase):
    pass


class CartUpdate(BaseModel):
    quantity: Optional[int] = None


class Cart(CartBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class CartWithProduct(Cart):
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    total_price: Optional[float] = None