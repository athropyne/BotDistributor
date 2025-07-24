import uuid
from pprint import pprint

import httpx
from fastapi import HTTPException, Depends

from src.core.config import settings
from src.core.infrastructures import portainer
from src.core.infrastructures.portainer import PortainerClient
from src.core.interfaces import BaseService
from src.services.distributor.dto.input import INPUT_NewBotParams

DOCKER_IMAGE = "telegram-bot"
ENDPOINT_ID = 3  # см. ниже, как получить


class SERVICE_PortainerManager(BaseService):
    def __init__(self,
                 portainer_client: PortainerClient = Depends(lambda: portainer)):
        super().__init__()
        self.portainer = portainer_client

    async def auth(self, username: str, password: str) -> str:
        return await self.portainer.auth(username, password)

    async def get_auth_header(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    async def get_environment_id(self, auth_header: dict):
        async with httpx.AsyncClient() as client:
            res = await client.get("http://localhost:9000/api/endpoints", headers=auth_header)
            for ep in res.json():
                if ep["Name"] == "local":
                    return ep["Id"]
            raise Exception("Endpoint 'local' not found")


async def get_env_list(headers):
    async with httpx.AsyncClient() as client:
        res = await client.get("http://localhost:9000/api/endpoints", headers=headers)
        for ep in res.json():
            if ep["Name"] == "local":
                return ep["Id"]
        raise Exception("Endpoint 'local' not found")


class SERVICE_DeployNewBot(BaseService):
    def __init__(self,
                 portainer_manager: SERVICE_PortainerManager = Depends()):
        super().__init__()
        self.portainer_manager = portainer_manager

    async def __call__(self, model: INPUT_NewBotParams):
        """Эта функция должна поднимать новый докер контейнер с TG ботом с указанными параметрами"""

        ##################
        import base64
        import json

        auth_config = {
            "username": "athropyne",
            "password": "dckr_pat_df8fBa7gznUpnHo1MC_h3r_eycE",
            "serveraddress": "https://index.docker.io/v1/"
        }
        encoded_auth = base64.b64encode(json.dumps(auth_config).encode()).decode()
        ####################

        container_name = f"telegram_bot_{uuid.uuid4().hex[:8]}"
        token = await self.portainer_manager.auth(settings.PORTAINER_USERNAME, settings.PORTAINER_PASSWORD)
        auth_header = await self.portainer_manager.get_auth_header(token)
        environment_id = await self.portainer_manager.get_environment_id(auth_header)

        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "Image": "athropyne/telegram-bot:latest",
            "Env": [f"BOT_TOKEN={model.bot_token}"],
            "HostConfig": {
                "RestartPolicy": {"Name": "unless-stopped"}
            }
        }
        r = await get_env_list(headers)
        timeout = httpx.Timeout(60.0, read=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Шаг 0: явно загрузить образ
            #     image_pull_url = f"http://localhost:9000/api/endpoints/{r}/docker/images/create?fromImage=athropyne/telegram-bot&tag=latest"
            # # async with httpx.AsyncClient() as client:
            #     pull_resp = await client.post(image_pull_url, headers=headers)
            #     if pull_resp.status_code != 200:
            #         raise HTTPException(status_code=500, detail=f"Failed to pull image: {pull_resp.text}")
            headers = {
                "Authorization": f"Bearer {token}",
                "X-Registry-Auth": encoded_auth
            }

            image_pull_url = f"http://localhost:9000/api/endpoints/{r}/docker/images/create?fromImage=athropyne/telegram-bot&tag=latest"
            pull_resp = await client.post(image_pull_url, headers=headers)
            # Шаг 1: создать контейнер
            create_url = f"http://localhost:9000/api/endpoints/{r}/docker/containers/create?name={container_name}"
            create_resp = await client.post(create_url, headers=headers, json=payload)
            if create_resp.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Create error: {create_resp.text}")

            container_id = create_resp.json()["Id"]

            # Шаг 2: запустить контейнер
            start_url = f"http://localhost:9000/api/endpoints/{r}/docker/containers/{container_id}/start"
            start_resp = await client.post(start_url, headers=headers)
            if start_resp.status_code != 204:
                raise HTTPException(status_code=500, detail=f"Start error: {start_resp.text}")

            return {"status": "ok", "container": container_name}
