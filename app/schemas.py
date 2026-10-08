"""Pydantic request / response schemas."""
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.config import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH
from app.models import RoleEnum

PHONE_PATTERN = re.compile(r"^\+?[0-9]{10,15}$")


def _clean_name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Full name must not be empty")
    return value


def _clean_phone(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = re.sub(r"[\s-]", "", value)
    if not PHONE_PATTERN.match(value):
        raise ValueError("Phone number must contain 10 to 15 digits, optionally starting with +")
    return value


class UserRegister(BaseModel):
    full_name: str = Field(..., max_length=100)
    email: EmailStr
    phone_number: Optional[str] = None
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    role: RoleEnum = RoleEnum.USER

    _name = field_validator("full_name")(_clean_name)
    _phone = field_validator("phone_number")(_clean_phone)

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    role: Optional[RoleEnum] = None

    @field_validator("full_name")
    @classmethod
    def name_not_blank(cls, v):
        if v is None:
            raise ValueError("Full name cannot be null")
        return _clean_name(v)

    @field_validator("email")
    @classmethod
    def email_not_null(cls, v):
        if v is None:
            raise ValueError("Email cannot be null")
        return v.lower()

    @field_validator("phone_number")
    @classmethod
    def phone_ok(cls, v):
        return _clean_phone(v)

    @field_validator("role")
    @classmethod
    def role_not_null(cls, v):
        if v is None:
            raise ValueError("Role cannot be null")
        return v


class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    role: RoleEnum
    created_date: datetime


class LoginResponse(BaseModel):
    message: str
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
