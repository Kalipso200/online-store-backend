from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.schemas.auth import User
from app.schemas.promotions import (
    Promotion, PromotionCreate, PromotionUpdate, PromotionWithUsage,
    PromotionUsage, ApplyPromoRequest, ApplyPromoResponse
)
from app.services.promotions import PromotionService, PromotionUsageService
from app.api.deps import get_db, get_current_admin_user
from app.services.csv_importer import CSVImporterService

router = APIRouter()


# ========== ADMIN ENDPOINTS ==========

@router.post("/", response_model=Promotion)
def create_promotion(
        promotion: PromotionCreate,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Создание промо-акции """
    return PromotionService.create_promotion(
        db=db,
        promotion=promotion,
        created_by=current_user.id
    )


@router.get("/", response_model=List[PromotionWithUsage])
def get_promotions(
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = Query(None),
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Получение списка промо-акций """
    promotions = PromotionService.get_promotions(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active
    )

    result = []
    for promo in promotions:
        promo_data = PromotionWithUsage.from_orm(promo)
        # Добавляем информацию об оставшихся использованиях
        if promo.usage_limit:
            promo_data.remaining_uses = promo.usage_limit - promo.used_count
        # Проверяем не истекла ли акция
        promo_data.is_expired = promo.end_date < datetime.now()
        result.append(promo_data)

    return result


@router.get("/{promotion_id}", response_model=Promotion)
def get_promotion_detail(
    promotion_id: int,
    db: Session = Depends(get_db)
):
    promotion = PromotionService.get_promotion(db, promotion_id)
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return promotion


@router.put("/{promotion_id}", response_model=Promotion)
def update_promotion(
        promotion_id: int,
        promotion_update: PromotionUpdate,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Обновление промо-акции """
    promotion = PromotionService.update_promotion(
        db=db,
        promotion_id=promotion_id,
        promotion_update=promotion_update
    )
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return promotion


@router.delete("/{promotion_id}")
def delete_promotion(
        promotion_id: int,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Удаление промо-акции """
    success = PromotionService.delete_promotion(db=db, promotion_id=promotion_id)
    if not success:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return {"message": "Promotion deleted successfully"}


@router.get("/{promotion_id}/usage", response_model=List[PromotionUsage])
def get_promotion_usage(
        promotion_id: int,
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Получение истории использования промо-кода """
    return PromotionService.get_promotion_usage(
        db=db,
        promotion_id=promotion_id,
        skip=skip,
        limit=limit
    )


@router.get("/{promotion_id}/stats")
def get_promotion_stats(
        promotion_id: int,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Получение статистики по промо-акции """
    stats = PromotionUsageService.get_usage_stats(db=db, promotion_id=promotion_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return stats


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


@router.get("/user/usage", response_model=List[PromotionUsage])
def get_user_promotion_usage(
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Получение истории использования промо-кодов пользователем"""
    return PromotionService.get_user_promotion_usage(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
@router.post("/import-csv", dependencies=[Depends(get_current_admin_user)])
def import_csv_data(db: Session = Depends(get_db)):
    """
    Принудительный импорт данных из CSV файла - только для администраторов
    """
    try:
        CSVImporterService.import_from_csv(db)
        return {"message": "Данные успешно импортированы из CSV файла"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка импорта: {str(e)}")


