from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Any

from app.api.deps import get_db, get_current_user
from app.schemas.auth import (
    Token, LoginRequest, RegisterRequest,
    ChangePasswordRequest, RefreshToken, User
)
from app.services.auth import UserService, AuthService

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=User)
def register(
        user_data: RegisterRequest,
        db: Session = Depends(get_db)
) -> Any:
    """
    Регистрация нового пользователя
    """
    user = UserService.create_user(db=db, user=user_data)
    return user


@router.post("/login", response_model=Token)
def login(
        login_data: LoginRequest,
        db: Session = Depends(get_db)
) -> Any:
    """
    Аутентификация пользователя и выдача токенов
    """
    user = UserService.authenticate_user(
        db, username=login_data.username, password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Создаем токены
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
        refresh_data: RefreshToken,
        db: Session = Depends(get_db)
) -> Any:
    """
    Обновление access токена с помощью refresh токена
    """
    payload = AuthService.verify_token(refresh_data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    user = UserService.get_user_by_id(db, user_id=int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Создаем новые токены
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }


@router.post("/change-password")
def change_password(
        password_data: ChangePasswordRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> Any:
    """
    Смена пароля текущего пользователя
    """
    success = UserService.change_password(
        db=db,
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    return {"message": "Password changed successfully"}


@router.get("/me", response_model=User)
def get_current_user_info(
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение информации о текущем пользователе
    """
    return current_user


@router.post("/logout")
def logout():
    """
    Выход из системы (на клиенте удаляются токены)
    """
    return {"message": "Successfully logged out"}