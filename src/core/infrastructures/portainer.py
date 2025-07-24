import httpx
from fastapi import HTTPException


class PortainerClient:
    def __init__(
            self,
            portainer_url: str
    ):
        self.portainer_url = portainer_url

    async def auth(self, username: str, password: str) -> str:
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(f"{self.portainer_url}/api/auth", json={
                "Username": username,
                "Password": password
            })
            print(resp.text)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Auth failed")
            return resp.json()["jwt"]