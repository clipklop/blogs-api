from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from blogs_api import models
from blogs_api.database import get_db
from blogs_api.schemas import UserLogin
from blogs_api.utils import verify_password

router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_login.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email or password")

    if not verify_password(user_login.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # TODO: Implement token generation and return the token instead of a success message
    return {"token": "Token generation not implemented yet", "message": "Login successful"}
