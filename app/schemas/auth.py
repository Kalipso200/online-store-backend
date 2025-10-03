from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from pydantic.functional_validators import field_validator
import re


class UserBase(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or '@' not in v:
            raise ValueError('Invalid email format')
        if len(v) > 100:
            raise ValueError('Email is too long')
        return v.strip().lower()

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Username cannot be empty')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username is too long')
        if ' ' in v:
            raise ValueError('Username cannot contain spaces')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers and underscores')
        return v.strip()

    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('First name cannot be empty')
        if len(v) > 50:
            raise ValueError('First name is too long')
        return v.strip()

    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Last name cannot be empty')
        if len(v) > 50:
            raise ValueError('Last name is too long')
        return v.strip()


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Password cannot be empty')
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        if len(v) > 128:
            raise ValueError('Password is too long')

        # Проверяем сложность пароля
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')

        # Проверяем на распространенные слабые пароли
        weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common and insecure')

        return v


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if '@' not in v:
                raise ValueError('Invalid email format')
            if len(v) > 100:
                raise ValueError('Email is too long')
            return v.strip().lower()
        return v

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('Username cannot be empty')
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if len(v) > 50:
                raise ValueError('Username is too long')
            if ' ' in v:
                raise ValueError('Username cannot contain spaces')
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('Username can only contain letters, numbers and underscores')
            return v.strip()
        return v

    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('First name cannot be empty')
            return v.strip()
        return v

    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('Last name cannot be empty')
            return v.strip()
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('Password cannot be empty')
            if len(v) < 12:
                raise ValueError('Password must be at least 12 characters long')
            if len(v) > 128:
                raise ValueError('Password is too long')

            if not re.search(r'[A-Z]', v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not re.search(r'[a-z]', v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one digit')
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
                raise ValueError('Password must contain at least one special character')

            weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
            if v.lower() in weak_passwords:
                raise ValueError('Password is too common and insecure')

        return v


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    hashed_password: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None


class RefreshToken(BaseModel):
    refresh_token: str


# Auth Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Username cannot be empty')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Password cannot be empty')
        return v


class RegisterRequest(UserCreate):
    pass


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator('current_password')
    @classmethod
    def validate_current_password(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Current password cannot be empty')
        return v

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('New password cannot be empty')
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        if len(v) > 128:
            raise ValueError('Password is too long')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')

        weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common and insecure')

        return v
