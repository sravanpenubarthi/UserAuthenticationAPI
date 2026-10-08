"""User management endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.models import RoleEnum

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[schemas.UserResponse])
def get_users(
    role: Optional[RoleEnum] = Query(None, description="Filter by role: Admin or User"),
    name: Optional[str] = Query(None, description="Search by full name (partial, case-insensitive)"),
    db: Session = Depends(get_db),
):
    return crud.list_users(db, role=role, name=name)


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, user_id)


@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(db, user_id, data)


@router.put("/{user_id}/password", response_model=schemas.MessageResponse)
def change_password(user_id: int, data: schemas.PasswordChange, db: Session = Depends(get_db)):
    crud.change_password(db, user_id, data)
    return {"message": "Password updated successfully"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    crud.delete_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
