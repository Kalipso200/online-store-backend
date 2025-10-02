from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.schemas.auth import User
from app.schemas.items import Cart, CartCreate, CartUpdate, CartWithProduct
from app.services.items import CartService

router = APIRouter()


@router.post("/", response_model=Cart)
def add_to_cart(
        cart_item: CartCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Добавление товара в корзину - только для авторизованных пользователей"""
    # Создаем словарь с данными и добавляем user_id
    cart_data = cart_item.dict()
    cart_data['user_id'] = current_user.id

    # Передаем данные в сервис
    return CartService.add_to_cart(db=db, cart_data=cart_data)


@router.get("/", response_model=List[CartWithProduct])
def get_user_cart(
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Просмотр корзины - только для авторизованных пользователей"""
    cart_items = CartService.get_user_cart(db=db, user_id=current_user.id, skip=skip, limit=limit)

    result = []
    for item in cart_items:
        cart_data = CartWithProduct.from_orm(item)
        cart_data.product_name = item.product.name if item.product else None
        cart_data.product_price = item.product.price if item.product else None
        cart_data.total_price = item.quantity * item.product.price if item.product else None
        result.append(cart_data)

    return result


@router.put("/{cart_id}", response_model=Cart)
def update_cart_item(
        cart_id: int,
        cart_update: CartUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Обновление товара в корзине - только владелец корзины"""
    db_cart = CartService.get_cart_item_by_id(db=db, cart_id=cart_id)
    if db_cart is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Проверяем, что пользователь является владельцем корзины
    if db_cart.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own cart items"
        )

    return CartService.update_cart_item(db=db, cart_id=cart_id, cart_update=cart_update)


@router.delete("/{cart_id}")
def remove_from_cart(
        cart_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Удаление товара из корзины - только владелец корзины"""
    db_cart = CartService.get_cart_item_by_id(db=db, cart_id=cart_id)
    if db_cart is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Проверяем, что пользователь является владельцем корзины
    if db_cart.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only remove your own cart items"
        )

    success = CartService.remove_from_cart(db=db, cart_id=cart_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}


@router.delete("/", response_model=dict)
def clear_cart(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Очистка корзины - только владелец корзины"""
    success = CartService.clear_user_cart(db=db, user_id=current_user.id)
    return {"message": "Cart cleared successfully"}