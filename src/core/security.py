import datetime
from datetime import timedelta, timezone
from enum import Enum, auto

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from starlette import status

from src.core import config
from src.core.exc import ExpiredSignatureError, InvalidTokenError, NotAuthorized
from src.core.types import ID

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
    def decode(cls, token: str = Depends(auth_scheme)) -> dict:
        try:
            payload: dict = jwt.decode(token, cls._TOKEN_SECRET_KEY, cls._ALGORITHM, options={"verify_sub": False})
            user_id = payload.get("id")
            if user_id is None:
                raise NotAuthorized(detail="Вы не авторизованы")
            return payload
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredSignatureError
        except jwt.InvalidTokenError:
            raise InvalidTokenError

    @classmethod
    def id(cls, token: str = Depends(auth_scheme)) -> ID:
        payload = cls.decode(token)
        return ID(payload["id"])
