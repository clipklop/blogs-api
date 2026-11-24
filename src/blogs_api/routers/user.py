from typing import Annotated, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, Depends, APIRouter, Query

from blogs_api import models, utils
from blogs_api.database import get_db
from blogs_api.oauth2 import get_current_user
from blogs_api.schemas import (
    UserCreate, UserResponse
)

DbSession = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: DbSession):
    db_user = models.User(**{**user.model_dump(), "password": utils.hash_password(user.password)})
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email address or username already exists."
        )

    return db_user

@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DbSession):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
    return user
