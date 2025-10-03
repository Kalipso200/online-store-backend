from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.schemas.auth import User
from app.schemas.promotions import (
    Promotion, PromotionCreate, PromotionUpdate, PromotionWithUsage,
    PromotionUsage, ApplyPromoRequest, ApplyPromoResponse
)
from app.services.promotions import PromotionService, PromotionUsageService

router = APIRouter()


@router.get("/public/active", response_model=List[Promotion])
def get_active_promotions(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Получение списка активных промо-акций - доступно всем"""
    try:
        # Получаем промо-акции из базы
        promotions = PromotionService.get_promotions(
            db=db,
            skip=skip,
            limit=limit,
            is_active=True
        )

        result = []
        for promo in promotions:
            try:
                # Создаем словарь с данными
                promo_data = {
                    "id": promo.id,
                    "title": promo.title,
                    "description": promo.description,
                    "promo_code": promo.promo_code,
                    "discount_type": promo.discount_type,
                    "discount_value": promo.discount_value,
                    "minimum_order_amount": promo.minimum_order_amount,
                    "maximum_discount": promo.maximum_discount,
                    "usage_limit": promo.usage_limit,
                    "user_usage_limit": promo.user_usage_limit,
                    "start_date": promo.start_date,
                    "end_date": promo.end_date,
                    "target_categories": promo.target_categories,
                    "target_products": promo.target_products,
                    "excluded_products": promo.excluded_products,
                    "is_active": promo.is_active,
                    "used_count": promo.used_count,
                    "created_at": promo.created_at,
                    "created_by": promo.created_by
                }

                promotion_schema = Promotion(**promo_data)
                result.append(promotion_schema)

            except Exception as e:
                print(f" Ошибка преобразования промо-акции {promo.id}: {e}")
                continue

        print(f"✅ Успешно преобразовано: {len(result)} промо-акций")
        return result

    except Exception as e:
        print(f" Критическая ошибка в эндпоинте: {e}")
        import traceback
        print(f" Трассировка: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/apply", response_model=ApplyPromoResponse)
def apply_promotion(
        request: ApplyPromoRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Применение промо-кода - только для авторизованных пользователей"""
    return PromotionService.apply_promotion(
        db=db,
        request=request,
        user_id=current_user.id
    )

