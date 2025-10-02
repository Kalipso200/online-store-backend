from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_admin_user
from app.schemas.items import Category, CategoryCreate, ProductWithCategory
from app.services.items import CategoryService, ProductService

router = APIRouter()

@router.post("/", response_model=Category, dependencies=[Depends(get_current_admin_user)])
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Создание категории - только для администраторов"""
    return CategoryService.create_category(db=db, category=category)

@router.get("/", response_model=List[Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Просмотр категорий - доступно всем"""
    return CategoryService.get_categories(db=db, skip=skip, limit=limit)

@router.get("/{category_id}", response_model=Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """Просмотр конкретной категории - доступно всем"""
    db_category = CategoryService.get_category(db=db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.delete("/{category_id}", dependencies=[Depends(get_current_admin_user)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Удаление категории - только для администраторов"""
    success = CategoryService.delete_category(db=db, category_id=category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}


@router.get("/{category_id}/products", response_model=List[ProductWithCategory])
def read_category_products(category_id: int, db: Session = Depends(get_db)):
    db_category = CategoryService.get_category(db=db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    products = ProductService.get_products(db=db, category_id=category_id)

    result = []
    for prod in products:
        product_data = ProductWithCategory.from_orm(prod)
        product_data.category_name = db_category.name
        result.append(product_data)
    return result


@router.delete("/{category_id}", dependencies=[Depends(get_current_admin_user)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Удаление категории - только для администраторов"""
    success = CategoryService.delete_category(db=db, category_id=category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}