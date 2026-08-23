from typing import Annotated, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, Depends, APIRouter, Query

from blogs_api import models, utils
from blogs_api.database import get_db
from blogs_api.schemas import (
    UserCreate, UserResponse
)

DbSession = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/users",
)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: DbSession):
    user.password = utils.hash_password(user.password)
    db_user = models.User(**user.model_dump())
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with the email address already exists."
        )

    return db_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DbSession):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
    return user
