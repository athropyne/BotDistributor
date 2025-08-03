import base64
import json
import uuid
from functools import wraps
from typing import Callable

import httpx
from fastapi import HTTPException
from httpx import AsyncClient
from loguru import logger
from starlette import status

from src.core.config import settings
from src.core.exc import (
    PortainerUnauthorized,
    ImageNotPulled,
    ContainerNotCreated,
    ContainerNotStarted, PortainerAuthFailed, EndpointsListNotReceived
)
from src.core.infrastructures import portainer
from src.core.interfaces import BaseService
from src.services.distributor.dto.input import INPUT_NewBotParams
from src.services.distributor.dto.output import OUTPUT_NewBotCreated
from src.services.distributor.exc import BotNotFound


def catch_portainer_unauthorized(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except PortainerUnauthorized:
            async with httpx.AsyncClient() as client:
                await auth(client)
                return await func(*args, **kwargs)

    return wrapper


async def auth(http_client: AsyncClient):
    url = f"{portainer.url}/api/auth"
    data = {
        "Username": portainer.username,
        "Password": portainer.password
    }
    response = await http_client.post(url, json=data)
    if response.status_code != status.HTTP_200_OK:
        logger.error(response.text)
        raise PortainerAuthFailed
    access_token = response.json()["jwt"]
    portainer.access_token = access_token
    return portainer.access_token


@catch_portainer_unauthorized
async def get_environment_id(client: AsyncClient) -> int:
    headers = {"Authorization": f"Bearer {portainer.access_token}"}
    response = await client.get(f"{settings.PORTAINER_URL}/api/endpoints", headers=headers)
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise PortainerUnauthorized
    if response.status_code != status.HTTP_200_OK:
        detail = response.text
        logger.error(detail)
        raise EndpointsListNotReceived(detail=detail)
    for ep in response.json():
        if ep["Name"] == "local":
            portainer.environment_id = ep["Id"]
            return portainer.environment_id
    raise Exception("Endpoint 'local' not found")


@catch_portainer_unauthorized
async def pull_image(
        http_client: AsyncClient,
):
    auth_config = {
        "username": f"{settings.DOCKERHUB_USERNAME}",
        "password": f"{settings.DOCKERHUB_PASSWORD}"
    }
    encoded_auth = base64.b64encode(json.dumps(auth_config).encode()).decode()
    headers = {
        "Authorization": f"Bearer {portainer.access_token}",
        "X-Registry-Auth": encoded_auth
    }

    image_pull_url = f"{portainer.url}/api/endpoints/{portainer.environment_id}/docker/images/create?fromImage={settings.IMAGE}"

    response = await http_client.post(image_pull_url, headers=headers)
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise PortainerUnauthorized
    if response.status_code != status.HTTP_200_OK:
        detail = response.text
        logger.error(detail)
        raise ImageNotPulled(detail=detail)
    logger.info(f"Image {settings.IMAGE} pulled")


@catch_portainer_unauthorized
async def create(
        client: AsyncClient,
        container_name: str,
        environment_id: int,
        bot_token: str,
        bot_title: str,
        bot_username: str,
        creator_id: int,
        bot_link: str):
    url = f"{settings.PORTAINER_URL}/api/endpoints/{environment_id}/docker/containers/create?name={container_name}"
    payload = {
        "Image": f"{settings.IMAGE}",
        "Env": [
            f"BOT_TOKEN={bot_token}",
            f"TITLE_BOT={bot_title}",
            f"USERNAME_BOT={bot_username}",
            f"CREATOR_USER_ID={creator_id}",
            f"BOT_LINK={bot_link}",

        ],
        "HostConfig": {
            "RestartPolicy": {"Name": "unless-stopped"}
        }
    }
    headers = {"Authorization": f"Bearer {portainer.access_token}"}
    response = await client.post(url, headers=headers, json=payload)
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise PortainerUnauthorized
    if response.status_code != status.HTTP_200_OK:
        detail = response.text
        logger.error(detail)
        raise ContainerNotCreated(detail=detail)

    container_id = response.json()["Id"]
    logger.info(f"Container {container_id} created")
    return container_id


@catch_portainer_unauthorized
async def start(client: AsyncClient,
                environment_id: int,
                container_id: str):
    start_url = f"{settings.PORTAINER_URL}/api/endpoints/{environment_id}/docker/containers/{container_id}/start"
    headers = {"Authorization": f"Bearer {portainer.access_token}"}
    response = await client.post(start_url, headers=headers)
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise PortainerUnauthorized
    if response.status_code != status.HTTP_204_NO_CONTENT:
        detail = response.text
        logger.error(detail)
        raise ContainerNotStarted(detail=detail)
    logger.info(f"Container {container_id} started")


async def check_valid_token(client: AsyncClient, bot_token: str):
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    response = await client.get(url)
    logger.debug(response.status_code)
    if response.status_code != status.HTTP_200_OK:
        logger.error(f"Bot {bot_token} not found")
        raise BotNotFound(bot_token)


class SERVICE_DeployNewBot(BaseService):
    async def __call__(self, model: INPUT_NewBotParams):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, read=60.0)) as client:
                await check_valid_token(client, model.bot_token)
                if not portainer.environment_id:
                    await get_environment_id(client)
                await pull_image(client)
                container_name = f"telegram_bot_{uuid.uuid4().hex[:8]}"
                container_id = await create(
                    client,
                    container_name,
                    portainer.environment_id,
                    model.bot_token,
                    model.bot_title,
                    model.bot_username,
                    model.creator_id,
                    model.bot_link
                )
                await start(client, portainer.environment_id, container_id)
                return OUTPUT_NewBotCreated(container_id=container_id, container_name=container_name)
        except httpx.ConnectError as e:
            logger.error("Portainer is not available")
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error. Portainer is not available"
            )
