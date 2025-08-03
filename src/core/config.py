from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')

    # server
    SERVER_HOST: str
    SERVER_PORT: int

    # portainer
    PORTAINER_URL: str = "http://localhost:9000"
    PORTAINER_USERNAME: str = "admin"
    PORTAINER_PASSWORD: str = "012345678910"
    PORTAINER_ENDPOINT_ID: int | None = 3

    # dockerhub
    DOCKERHUB_USERNAME: str | None = "athropyne"
    DOCKERHUB_PASSWORD: str | None = "dckr_pat_2yHx97iNNAiHOmZ5byIH5F0jVBs"
    IMAGE: str

    # admin panel
    ADMIN_PANEL_USERNAME: str
    ADMIN_PANEL_PASSWORD: str

    # access token
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    TOKEN_SECRET_KEY: str


settings = Settings()
