"""Registration and login endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: schemas.UserRegister, db: Session = Depends(get_db)):
    return crud.create_user(db, data)


@router.post("/login", response_model=schemas.LoginResponse, status_code=status.HTTP_200_OK)
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, data)
    return {"message": "Login successful", "user": user}
