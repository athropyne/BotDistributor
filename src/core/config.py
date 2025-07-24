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

    # dockerhub
    DOCKERHUB_USERNAME: str
    DOCKERHUB_PASSWORD: str  # password or token
    IMAGE: str
    SERVER_ADDRESS: str = "https://index.docker.io/v1/"


settings = Settings()
