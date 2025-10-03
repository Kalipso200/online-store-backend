from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi import status

from app.api.deps import get_db, get_current_user
from app.schemas.auth import User
from app.schemas.items import Review, ReviewCreate, ReviewUpdate, ReviewWithUser
from app.services.items import ReviewService

router = APIRouter()


@router.post("/", response_model=Review)
def create_review(
        review: ReviewCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Создание отзыва - только для авторизованных пользователей"""
    # Создаем словарь с данными и добавляем user_id
    review_data = review.dict()
    review_data['user_id'] = current_user.id

    return ReviewService.create_review(db=db, review_data=review_data)


@router.get("/product/{product_id}", response_model=List[ReviewWithUser])
def read_product_reviews(
        product_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Просмотр отзывов товара - доступно всем"""
    reviews = ReviewService.get_reviews_by_product(
        db=db, product_id=product_id, skip=skip, limit=limit
    )

    result = []
    for review in reviews:
        review_data = ReviewWithUser.from_orm(review)
        review_data.username = review.user.username if review.user else None
        review_data.first_name = review.user.first_name if review.user else None
        review_data.last_name = review.user.last_name if review.user else None
        result.append(review_data)

    return result


@router.get("/user/{user_id}", response_model=List[Review])
def read_user_reviews(
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Просмотр отзывов пользователя - доступно всем"""
    return ReviewService.get_reviews_by_user(
        db=db, user_id=user_id, skip=skip, limit=limit
    )


@router.put("/{review_id}", response_model=Review)
def update_review(
        review_id: int,
        review: ReviewUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Обновление отзыва - только автор отзыва"""
    db_review = ReviewService.get_review_by_id(db=db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    # Проверяем, что пользователь является автором отзыва
    if db_review.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews"
        )

    return ReviewService.update_review(db=db, review_id=review_id, review_update=review)


@router.delete("/{review_id}")
def delete_review(
        review_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Удаление отзыва - автор отзыва или администратор"""
    db_review = ReviewService.get_review_by_id(db=db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    # Проверяем, что пользователь является автором отзыва или администратором
    if db_review.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )

    success = ReviewService.delete_review(db=db, review_id=review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}