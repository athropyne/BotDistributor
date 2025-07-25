from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')

    # server
    SERVER_HOST: str
    SERVER_PORT: int

    # portainer
    PORTAINER_URL: str
    PORTAINER_USERNAME: str
    PORTAINER_PASSWORD: str
    PORTAINER_ENDPOINT_ID: int | None = None

    # dockerhub
    DOCKERHUB_USERNAME: str | None = None
    DOCKERHUB_PASSWORD: str | None = None
    IMAGE: str

    # admin panel
    ADMIN_PANEL_USERNAME: str
    ADMIN_PANEL_PASSWORD: str

    # access token
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    TOKEN_SECRET_KEY: str


settings = Settings()
