import httpx
from fastapi import HTTPException
from loguru import logger
from starlette import status

from src.core.config import settings
from src.core.exc import PortainerAuthFailed, PortainerUnauthorized


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

    async def auth(self) -> str:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(f"{self.url}/api/auth", json={
                "Username": self.username,
                "Password": self.password
            })
            if response.status_code != 200:
                raise PortainerAuthFailed
            self.access_token = response.json()["jwt"]
            return self.access_token

    async def get_environment_id(self, auth_header: dict) -> int:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.PORTAINER_URL}/api/endpoints", headers=auth_header)
            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                logger.debug(response.json())
                await self.auth()
                logger.debug("Successful reauth")
            for ep in response.json():
                if ep["Name"] == "local":
                    self.environment_id = ep["Id"]
                    return self.environment_id
            raise Exception("Endpoint 'local' not found")

    async def init(self):
        try:
            await self.auth()
            if settings.PORTAINER_ENDPOINT_ID is None:
                await self.get_environment_id({"Authorization": f"Bearer {self.access_token}"})
            else:
                self.environment_id = settings.PORTAINER_ENDPOINT_ID
        except (httpx.ConnectError, httpx.InvalidURL) as e:
            logger.error("Invalid Portainer URL")
            raise RuntimeError("Portainer is not available. Invalid Portainer URL")
        except PortainerAuthFailed as e:
            logger.error(e.detail)
            raise
        async with httpx.AsyncClient() as client:
            pass
