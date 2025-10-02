from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status

from app.models.models import Promotion, PromotionUsage, Product
from app.schemas.promotions import PromotionCreate, PromotionUpdate, ApplyPromoRequest, ApplyPromoResponse


class PromotionService:
    @staticmethod
    def get_promotions(
            db: Session,
            skip: int = 0,
            limit: int = 100,
            is_active: Optional[bool] = None
    ) -> List[Promotion]:
        query = db.query(Promotion)

        if is_active is not None:
            query = query.filter(Promotion.is_active == is_active)

        promotions = query.offset(skip).limit(limit).all()

        # Преобразуем в Pydantic схемы
        from app.schemas.promotions import Promotion as PromotionSchema
        return [PromotionSchema.from_orm(promo) for promo in promotions]

    @staticmethod
    def get_promotion(db: Session, promotion_id: int) -> Optional[Promotion]:
        return db.query(Promotion).filter(Promotion.id == promotion_id).first()

    @staticmethod
    def get_promotion_by_code(db: Session, promo_code: str) -> Optional[Promotion]:
        return db.query(Promotion).filter(Promotion.promo_code == promo_code).first()

    @staticmethod
    def create_promotion(db: Session, promotion: PromotionCreate, created_by: int) -> Promotion:
        # Проверяем уникальность промо-кода
        existing_promo = PromotionService.get_promotion_by_code(db, promotion.promo_code)
        if existing_promo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promo code already exists"
            )

        db_promotion = Promotion(
            **promotion.dict(),
            created_by=created_by
        )
        db.add(db_promotion)
        db.commit()
        db.refresh(db_promotion)
        return db_promotion

    @staticmethod
    def update_promotion(db: Session, promotion_id: int, promotion_update: PromotionUpdate) -> Optional[Promotion]:
        db_promotion = PromotionService.get_promotion(db, promotion_id)
        if not db_promotion:
            return None

        try:
            update_data = promotion_update.dict(exclude_unset=True)

            # Валидация дат
            if 'start_date' in update_data or 'end_date' in update_data:
                start_date = update_data.get('start_date', db_promotion.start_date)
                end_date = update_data.get('end_date', db_promotion.end_date)
                if end_date <= start_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='End date must be after start date'
                    )

            # Валидация скидки
            if 'discount_value' in update_data:
                discount_type = update_data.get('discount_type', db_promotion.discount_type)
                discount_value = update_data['discount_value']

                if discount_type in ["percentage", "fixed"] and discount_value is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Discount value is required for percentage and fixed discounts'
                    )

                if discount_type == "percentage" and discount_value is not None:
                    if discount_value <= 0 or discount_value > 100:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Percentage discount must be between 0 and 100'
                        )

                if discount_type == "fixed" and discount_value is not None:
                    if discount_value <= 0:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Fixed discount must be greater than 0'
                        )

            # Обновление полей
            for field, value in update_data.items():
                setattr(db_promotion, field, value)

            db.commit()
            db.refresh(db_promotion)
            return db_promotion

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating promotion: {str(e)}"
            )

    @staticmethod
    def delete_promotion(db: Session, promotion_id: int) -> bool:
        db_promotion = PromotionService.get_promotion(db, promotion_id)
        if db_promotion:
            db.delete(db_promotion)
            db.commit()
            return True
        return False

    @staticmethod
    def apply_promotion(db: Session, request: ApplyPromoRequest, user_id: int) -> ApplyPromoResponse:
        """Применение промо-кода к заказу"""
        promotion = PromotionService.get_promotion_by_code(db, request.promo_code)

        if not promotion:
            return ApplyPromoResponse(
                valid=False,
                message="Promo code not found"
            )

        # Проверяем активность акции
        if not promotion.is_active:
            return ApplyPromoResponse(
                valid=False,
                message="Promotion is not active"
            )

        # Проверяем даты действия
        now = datetime.now()
        if now < promotion.start_date or now > promotion.end_date:
            return ApplyPromoResponse(
                valid=False,
                message="Promotion is expired or not yet started"
            )

        # Проверяем лимит использований
        if promotion.usage_limit and promotion.used_count >= promotion.usage_limit:
            return ApplyPromoResponse(
                valid=False,
                message="Promotion usage limit reached"
            )

        # Проверяем лимит использований на пользователя
        user_usage_count = db.query(PromotionUsage).filter(
            PromotionUsage.promotion_id == promotion.id,
            PromotionUsage.user_id == user_id
        ).count()

        if user_usage_count >= promotion.user_usage_limit:
            return ApplyPromoResponse(
                valid=False,
                message="You have already used this promotion"
            )

        # Проверяем минимальную сумму заказа
        if request.total_amount < promotion.minimum_order_amount:
            return ApplyPromoResponse(
                valid=False,
                message=f"Minimum order amount is {promotion.minimum_order_amount}"
            )

        # Проверяем applicability к товарам
        if not PromotionService._is_applicable_to_products(db, promotion, request.product_ids):
            return ApplyPromoResponse(
                valid=False,
                message="Promotion is not applicable to selected products"
            )

        # Рассчитываем скидку
        discount_amount = PromotionService._calculate_discount(promotion, request.total_amount)

        return ApplyPromoResponse(
            valid=True,
            discount_amount=discount_amount,
            final_amount=request.total_amount - discount_amount,
            message="Promotion applied successfully",
            promotion=promotion
        )

    @staticmethod
    def _is_applicable_to_products(db: Session, promotion: Promotion, product_ids: List[int]) -> bool:
        """Проверяет применимость акции к выбранным товарам"""
        if not product_ids:
            return True

        # Если указаны целевые категории/товары, проверяем соответствие
        if promotion.target_categories:
            # Получаем товары из целевых категорий
            target_products = db.query(Product.id).filter(
                Product.category_id.in_(promotion.target_categories)
            ).all()
            target_product_ids = [p.id for p in target_products]

            # Проверяем, что все товары входят в целевые
            if not all(pid in target_product_ids for pid in product_ids):
                return False

        if promotion.target_products:
            # Проверяем, что все товары входят в целевые
            if not all(pid in promotion.target_products for pid in product_ids):
                return False

        # Проверяем исключенные товары
        if promotion.excluded_products:
            if any(pid in promotion.excluded_products for pid in product_ids):
                return False

        return True

    @staticmethod
    def _calculate_discount(promotion: Promotion, total_amount: float) -> float:
        """Рассчитывает сумму скидки"""
        if promotion.discount_type == "free_shipping":
            # Логика бесплатной доставки
            return 0  # В реальном приложении возвращаем стоимость доставки

        elif promotion.discount_type == "percentage":
            discount = total_amount * (promotion.discount_value / 100)
            if promotion.maximum_discount:
                discount = min(discount, promotion.maximum_discount)
            return discount

        elif promotion.discount_type == "fixed":
            return min(promotion.discount_value, total_amount)

        return 0

    @staticmethod
    def record_promotion_usage(
            db: Session,
            promotion_id: int,
            user_id: int,
            discount_amount: float,
            order_id: Optional[int] = None
    ) -> PromotionUsage:
        """Записывает использование промо-кода"""
        promotion = PromotionService.get_promotion(db, promotion_id)
        if promotion:
            promotion.used_count += 1

        usage = PromotionUsage(
            promotion_id=promotion_id,
            user_id=user_id,
            order_id=order_id,
            discount_amount=discount_amount
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)
        return usage

    @staticmethod
    def get_promotion_usage(db: Session, promotion_id: int, skip: int = 0, limit: int = 100) -> List[PromotionUsage]:
        return db.query(PromotionUsage).filter(
            PromotionUsage.promotion_id == promotion_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_promotion_usage(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[PromotionUsage]:
        return db.query(PromotionUsage).filter(
            PromotionUsage.user_id == user_id
        ).offset(skip).limit(limit).all()


class PromotionUsageService:
    @staticmethod
    def get_usage_stats(db: Session, promotion_id: int) -> Dict[str, Any]:
        """Получает статистику использования промо-кода"""
        promotion = PromotionService.get_promotion(db, promotion_id)
        if not promotion:
            return {}

        total_usage = promotion.used_count
        total_discount = db.query(db.func.sum(PromotionUsage.discount_amount)).filter(
            PromotionUsage.promotion_id == promotion_id
        ).scalar() or 0

        return {
            "promotion_id": promotion_id,
            "total_usage": total_usage,
            "total_discount": total_discount,
            "remaining_uses": promotion.usage_limit - total_usage if promotion.usage_limit else None,
            "usage_percentage": (total_usage / promotion.usage_limit * 100) if promotion.usage_limit else None
        }