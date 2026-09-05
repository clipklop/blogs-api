from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Depends, status

from blogs_api.schemas import TokenData

SECRET_KEY = "1e161ee6687d59903b9c7776c7c23e6d2a9f47a93b25ef447b733e456230a66e"  # Replace with your actual secret key, like with openssl rand -hex 32
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise ValueError("Invalid token: user_id not found")
        return TokenData(id=user_id)
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def get_current_user(token: str):
    try:
        token_data = verify_access_token(token)
        return token_data
    except ValueError as e:
        raise ValueError(f"Token verification failed: {str(e)}")
