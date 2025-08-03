import json
from functools import wraps
from typing import Callable

import httpx
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from httpx import Response
from loguru import logger
from starlette import status

from src.services.auth.dto.input import INPUT_AuthData


def catch_failed_httpx_connection(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except httpx.ConnectError as e:
            logger.error("Portainer is not available")
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error. Portainer is not available"
            )

    return wrapper


def parse_response(response: Response):
    try:
        detail = response.json()["message"]
    except json.decoder.JSONDecodeError:
        detail = response.text
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Response parsing error")
    return detail


def convert_auth_data(data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    return INPUT_AuthData(login=data.username, password=data.password)
