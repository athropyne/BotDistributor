import datetime
from datetime import timedelta, timezone

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from starlette import status

from src.core import config
from src.core.exc import ExpiredSignatureError, InvalidTokenError

auth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class TokenManager:
    _ALGORITHM = "HS256"
    _TOKEN_SECRET_KEY = config.settings.TOKEN_SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES = config.settings.ACCESS_TOKEN_EXPIRE_MINUTES

    @classmethod
    def create(cls, data: dict | None) -> str:
        to_encode = {} if data is None else data.copy()
        expire_delta = timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.datetime.now(tz=timezone.utc) + expire_delta
        to_encode.update({"exp": expire})
        try:
            jwt_str = jwt.encode(to_encode, cls._TOKEN_SECRET_KEY, cls._ALGORITHM)
            return jwt_str
        except:
            logger.error("Failed to create an access token due to a server error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create an access token due to a server error"
            )

    @classmethod
    def decode(cls, token: str = Depends(auth_scheme)) -> None:
        try:
            jwt.decode(token, cls._TOKEN_SECRET_KEY, cls._ALGORITHM, options={"verify_sub": False})
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredSignatureError
        except jwt.InvalidTokenError:
            raise InvalidTokenError
