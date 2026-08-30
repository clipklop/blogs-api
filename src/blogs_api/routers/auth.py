from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from blogs_api.database import get_db
from blogs_api.schemas import UserLogin

router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    # furher implementation for user authentication would go here
    return {"message": "Login successful"}
