from pydantic import BaseModel, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    FREE_SHIPPING = "free_shipping"


class PromotionBase(BaseModel):
    title: str
    description: Optional[str] = None
    promo_code: str
    discount_type: DiscountType
    discount_value: Optional[float] = None
    minimum_order_amount: float = 0
    maximum_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    user_usage_limit: int = 1
    start_date: datetime
    end_date: datetime
    target_categories: Optional[List[int]] = None
    target_products: Optional[List[int]] = None
    excluded_products: Optional[List[int]] = None
    is_active: bool = True

    @field_validator('discount_value')
    @classmethod
    def validate_discount_value(cls, v: Optional[float], validation_info):
        if validation_info.data and 'discount_type' in validation_info.data:
            discount_type = validation_info.data['discount_type']

            if discount_type in [DiscountType.PERCENTAGE, DiscountType.FIXED] and v is None:
                raise ValueError('Discount value is required for percentage and fixed discounts')

            if discount_type == DiscountType.PERCENTAGE and v is not None:
                # ИЗМЕНЕНИЕ: разрешаем 0 для процентной скидки
                if v < 0 or v > 100:
                    raise ValueError('Percentage discount must be between 0 and 100')

            if discount_type == DiscountType.FIXED and v is not None:
                # ИЗМЕНЕНИЕ: разрешаем 0 для фиксированной скидки
                if v < 0:
                    raise ValueError('Fixed discount must be greater than or equal to 0')

        return v

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v: datetime, validation_info):
        if validation_info.data and 'start_date' in validation_info.data:
            start_date = validation_info.data['start_date']
            if v < start_date:
                raise ValueError('End date must be after start date')
        return v


class PromotionCreate(PromotionBase):
    @field_validator('promo_code')
    @classmethod
    def validate_promo_code(cls, v: str):
        if not v or not v.strip():
            raise ValueError('Promo code cannot be empty')
        if len(v) < 3:
            raise ValueError('Promo code must be at least 3 characters long')
        return v.strip().upper()

    @field_validator('start_date', 'end_date', mode='before')
    @classmethod
    def validate_date_format(cls, v):
        """Преобразует строку в datetime если необходимо"""
        if isinstance(v, str):
            try:
                # Пробуем разные форматы дат
                if 'T' in v:
                    return datetime.fromisoformat(v.replace('Z', '+00:00'))
                else:
                    return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('Invalid date format. Use ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS')
        return v


class PromotionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    discount_value: Optional[float] = None
    minimum_order_amount: Optional[float] = None
    maximum_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    user_usage_limit: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_categories: Optional[List[int]] = None
    target_products: Optional[List[int]] = None
    excluded_products: Optional[List[int]] = None
    is_active: Optional[bool] = None


class Promotion(PromotionBase):
    id: int
    used_count: int = 0
    created_at: datetime
    created_by: int

    model_config = ConfigDict(from_attributes=True)


class PromotionWithUsage(Promotion):
    remaining_uses: Optional[int] = None
    is_expired: bool = False


class PromotionUsageBase(BaseModel):
    promotion_id: int
    user_id: int
    order_id: Optional[int] = None
    discount_amount: float


class PromotionUsageCreate(PromotionUsageBase):
    pass


class PromotionUsage(PromotionUsageBase):
    id: int
    used_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplyPromoRequest(BaseModel):
    promo_code: str
    product_ids: List[int] = []
    total_amount: float


class ApplyPromoResponse(BaseModel):
    valid: bool
    discount_amount: float = 0
    final_amount: float = 0
    message: Optional[str] = None
    promotion: Optional[Promotion] = None