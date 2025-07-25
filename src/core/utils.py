import json
from functools import wraps
from typing import Callable

import httpx
from fastapi import HTTPException
from httpx import Response
from loguru import logger
from starlette import status

from src.core.exc import PortainerUnauthorized
from src.core.infrastructures import portainer


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


def catch_portainer_unauthorized(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except PortainerUnauthorized:
            await portainer.auth()
            return await func(*args, **kwargs)

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
