import httpx
from httpx import AsyncClient
from loguru import logger
from starlette import status

from src.core.config import settings
from src.core.exc import PortainerAuthFailed, EndpointsListNotReceived
from src.core.utils import parse_response, catch_portainer_unauthorized


class PortainerClient:
    def __init__(
            self,
            portainer_url: str,
            portainer_username: str,
            portainer_password: str,
            portainer_environment_id: int | None = None
    ):
        self.url = portainer_url
        self.username = portainer_username
        self.password = portainer_password
        self.access_token: str | None = None
        self.environment_id: int | None = portainer_environment_id

    async def auth(self, client: AsyncClient) -> str:
        response = await client.post(f"{self.url}/api/auth", json={
            "Username": self.username,
            "Password": self.password
        })
        if response.status_code != status.HTTP_200_OK:
            logger.error(parse_response(response))
            raise PortainerAuthFailed
        self.access_token = response.json()["jwt"]
        return self.access_token

    @catch_portainer_unauthorized
    async def get_environment_id(self, client: AsyncClient, auth_header: dict) -> int:
        response = await client.get(f"{settings.PORTAINER_URL}/api/endpoints", headers=auth_header)
        if response.status_code != status.HTTP_200_OK:
            detail = parse_response(response)
            logger.error(detail)
            raise EndpointsListNotReceived(detail=detail)
        for ep in response.json():
            if ep["Name"] == "local":
                self.environment_id = ep["Id"]
                return self.environment_id
        raise Exception("Endpoint 'local' not found")

    async def init(self):
        async with httpx.AsyncClient() as client:
            try:
                await self.auth(client)
                if settings.PORTAINER_ENDPOINT_ID is None:
                    await self.get_environment_id(client, {"Authorization": f"Bearer {self.access_token}"})
                else:
                    self.environment_id = settings.PORTAINER_ENDPOINT_ID
            except (httpx.ConnectError, httpx.InvalidURL) as e:
                logger.error("Invalid Portainer URL")
                raise RuntimeError("Portainer is not available. Invalid Portainer URL")
            except PortainerAuthFailed as e:
                logger.error(e.detail)
                raise


