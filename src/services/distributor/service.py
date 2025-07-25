import base64
import json
import uuid

import httpx
from fastapi import Depends
from httpx import AsyncClient
from loguru import logger
from starlette import status

from src.core.config import settings
from src.core.exc import InvalidURL, DockerhubAuthFailed, PortainerUnauthorized, ImageNotPulled, ContainerNotCreated, \
    ContainerNotStarted
from src.core.infrastructures import portainer
from src.core.infrastructures.portainer import PortainerClient
from src.core.interfaces import BaseService
from src.core.utils import catch_failed_httpx_connection, catch_portainer_unauthorized, parse_response
from src.services.distributor.dto.input import INPUT_NewBotParams
from src.services.distributor.dto.output import OUTPUT_NewBotCreated
from src.services.distributor.exc import BotNotFound


class SERVICE_BotContainerManager:
    def __init__(self,
                 portainer_client: PortainerClient = Depends(lambda: portainer)):
        super().__init__()
        self.portainer = portainer_client

    @catch_failed_httpx_connection
    @catch_portainer_unauthorized
    async def pull_image(self,
                         client: AsyncClient,
                         token: str
                         ):
        auth_config = {
            "username": f"{settings.DOCKERHUB_USERNAME}",
            "password": f"{settings.DOCKERHUB_PASSWORD}"
        }
        encoded_auth = base64.b64encode(json.dumps(auth_config).encode()).decode()
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Registry-Auth": encoded_auth
        }

        image_pull_url = f"{settings.PORTAINER_URL}/api/endpoints/{portainer.environment_id}/docker/images/create?fromImage={settings.IMAGE}"

        pull_resp = await client.post(image_pull_url, headers=headers)
        if pull_resp.status_code != status.HTTP_200_OK:
            logger.debug(pull_resp.status_code)
            logger.debug(pull_resp.text)
            detail = parse_response(pull_resp)
            match pull_resp.status_code:
                case status.HTTP_500_INTERNAL_SERVER_ERROR:
                    raise DockerhubAuthFailed(detail)
                case status.HTTP_404_NOT_FOUND:
                    raise InvalidURL(detail)
                case status.HTTP_401_UNAUTHORIZED:
                    raise PortainerUnauthorized
                case _:
                    raise ImageNotPulled(detail)
        logger.info(f"Image {settings.IMAGE} pulled")

    @catch_failed_httpx_connection
    @catch_portainer_unauthorized
    async def create(self,
                     client: AsyncClient,
                     environment_id: int,
                     bot_token: str,
                     headers: dict):
        container_name = f"telegram_bot_{uuid.uuid4().hex[:8]}"
        create_url = f"{settings.PORTAINER_URL}/api/endpoints/{environment_id}/docker/containers/create?name={container_name}"
        payload = {
            "Image": f"{settings.IMAGE}",
            "Env": [f"BOT_TOKEN={bot_token}"],
            "HostConfig": {
                "RestartPolicy": {"Name": "unless-stopped"}
            }
        }
        create_resp = await client.post(create_url, headers=headers, json=payload)
        if create_resp.status_code != 200:
            logger.debug(create_resp.status_code)
            logger.debug(create_resp.text)

            detail = parse_response(create_resp)
            match create_resp.status_code:
                case status.HTTP_404_NOT_FOUND:
                    raise InvalidURL(detail)
                case status.HTTP_401_UNAUTHORIZED:
                    raise PortainerUnauthorized
                case _:
                    raise ContainerNotCreated

        container_id = create_resp.json()["Id"]
        logger.info(f"Container {container_id} created")
        return container_id, container_name

    @catch_failed_httpx_connection
    @catch_portainer_unauthorized
    async def start(self,
                    client: AsyncClient,
                    environment_id: int,
                    container_id: str,
                    headers: dict):
        start_url = f"{settings.PORTAINER_URL}/api/endpoints/{environment_id}/docker/containers/{container_id}/start"
        start_resp = await client.post(start_url, headers=headers)
        if start_resp.status_code != 204:
            logger.debug(start_resp.status_code)
            logger.debug(start_resp.text)
            detail = parse_response(start_resp)
            match start_resp.status_code:
                case status.HTTP_404_NOT_FOUND:
                    raise InvalidURL(detail)
                case status.HTTP_401_UNAUTHORIZED:
                    raise PortainerUnauthorized
                case _:
                    raise ContainerNotStarted
        logger.info(f"Container {container_id} started")


class SERVICE_DeployNewBot(BaseService):
    def __init__(self,
                 portainer_client: PortainerClient = Depends(lambda: portainer),
                 container_manager: SERVICE_BotContainerManager = Depends()):
        super().__init__()
        self.portainer_client = portainer_client
        self.container_manager = container_manager

    async def __call__(self, model: INPUT_NewBotParams):
        headers = {"Authorization": f"Bearer {portainer.access_token}"}

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, read=60.0)) as client:
            url = f"https://api.telegram.org/bot{model.bot_token}/getMe"
            response = await client.get(url)
            if response.status_code != status.HTTP_200_OK:
                logger.error(f"Bot {model.bot_token} not found")
                raise BotNotFound(model.bot_token)

            await self.container_manager.pull_image(
                client,
                portainer.access_token
            )
            container_id, container_name = await self.container_manager.create(
                client,
                portainer.environment_id,
                model.bot_token,
                headers
            )
            await self.container_manager.start(client, portainer.environment_id, container_id, headers)
            return OUTPUT_NewBotCreated(container_id=container_id, container_name=container_name)
