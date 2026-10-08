"""Database operations and password hashing."""
from typing import Optional

import bcrypt
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.exceptions import (
    EmailAlreadyExistsError,
    EmptyUpdateError,
    IncorrectPasswordError,
    InvalidCredentialsError,
    UserNotFoundError,
)


# ---------- password helpers ----------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


# ---------- reads ----------
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email.lower()).first()


def get_user(db: Session, user_id: int) -> models.User:
    user = db.get(models.User, user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return user


def list_users(
    db: Session,
    role: Optional[models.RoleEnum] = None,
    name: Optional[str] = None,
) -> list[models.User]:
    query = db.query(models.User)
    if role is not None:
        query = query.filter(models.User.role == role)
    if name:
        query = query.filter(func.lower(models.User.full_name).like(f"%{name.strip().lower()}%"))
    return query.order_by(models.User.user_id).all()


# ---------- writes ----------
def create_user(db: Session, data: schemas.UserRegister) -> models.User:
    if get_user_by_email(db, data.email):
        raise EmailAlreadyExistsError()
    user = models.User(
        full_name=data.full_name,
        email=data.email,
        phone_number=data.phone_number,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExistsError()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: schemas.UserLogin) -> models.User:
    user = get_user_by_email(db, data.email)
    # Same error for unknown email and wrong password, so attackers can't enumerate emails.
    if not user or not verify_password(data.password, user.password_hash):
        raise InvalidCredentialsError()
    return user


def update_user(db: Session, user_id: int, data: schemas.UserUpdate) -> models.User:
    user = get_user(db, user_id)
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise EmptyUpdateError()

    new_email = changes.get("email")
    if new_email and new_email != user.email:
        if get_user_by_email(db, new_email):
            raise EmailAlreadyExistsError()

    for field, value in changes.items():
        setattr(user, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExistsError()
    db.refresh(user)
    return user


def change_password(db: Session, user_id: int, data: schemas.PasswordChange) -> None:
    user = get_user(db, user_id)
    if not verify_password(data.old_password, user.password_hash):
        raise IncorrectPasswordError()
    user.password_hash = hash_password(data.new_password)
    db.commit()


def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()
