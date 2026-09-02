from datetime import datetime, timedelta

import jwt

SECRET_KEY = "1e161ee6687d59903b9c7776c7c23e6d2a9f47a93b25ef447b733e456230a66e"  # Replace with your actual secret key, like with openssl rand -hex 32
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
