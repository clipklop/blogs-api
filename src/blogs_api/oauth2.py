from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from blogs_api import models
from blogs_api.database import get_db
from blogs_api.schemas import TokenData
from blogs_api.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp", "user_id"]})
        user_id = payload["user_id"]
        if type(user_id) is not int or user_id <= 0:
            raise credentials_exception
        return TokenData(id=user_id)
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise credentials_exception

def invalid_credentials():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = verify_access_token(token, invalid_credentials())
    user = db.get(models.User, token_data.id)
    if user is None:
        raise invalid_credentials()
    return user


def resolve_post_reader(request: Request, db: Session, token: str | None, *, required: bool = False):
    if not required and "Authorization" not in request.headers:
        return None
    if not token:
        raise invalid_credentials()
    return get_current_user(token, db)
