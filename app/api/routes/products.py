from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_admin_user
from app.schemas.items import Product, ProductCreate, ProductUpdate, ProductWithCategory
from app.services.items import ProductService

router = APIRouter()


@router.post("/", response_model=Product, dependencies=[Depends(get_current_admin_user)])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Создание товара - только для администраторов"""
    return ProductService.create_product(db=db, product=product)


@router.get("/", response_model=List[ProductWithCategory])
def read_products(
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = Query(None),
        min_price: Optional[float] = Query(None),
        max_price: Optional[float] = Query(None),
        min_rating: Optional[float] = Query(None),
        db: Session = Depends(get_db)
):
    """Просмотр товаров - доступно всем"""
    products = ProductService.get_products(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating
    )

    result = []
    for prod in products:
        product_data = ProductWithCategory.from_orm(prod)
        product_data.category_name = prod.category.name if prod.category else None
        result.append(product_data)

    return result


@router.get("/{product_id}", response_model=ProductWithCategory)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """Просмотр конкретного товара - доступно всем"""
    db_product = ProductService.get_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product_data = ProductWithCategory.from_orm(db_product)
    product_data.category_name = db_product.category.name if db_product.category else None
    return product_data


@router.put("/{product_id}", response_model=Product, dependencies=[Depends(get_current_admin_user)])
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """Обновление товара - только для администраторов"""
    db_product = ProductService.update_product(db=db, product_id=product_id, product_update=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.delete("/{product_id}", dependencies=[Depends(get_current_admin_user)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Удаление товара - только для администраторов"""
    success = ProductService.delete_product(db=db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}