from pydantic import BaseModel

from src.core.config import settings


class Portainer(BaseModel):
    url: str = settings.PORTAINER_URL
    username: str = settings.PORTAINER_USERNAME
    password: str = settings.PORTAINER_PASSWORD
    access_token: str | None = None
    environment_id: int | None = None
