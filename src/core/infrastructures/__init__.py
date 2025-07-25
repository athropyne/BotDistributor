from src.core.config import settings
from src.core.infrastructures.http_client import HttpClient
from src.core.infrastructures.portainer import PortainerClient

portainer = PortainerClient(
    settings.PORTAINER_URL,
    settings.PORTAINER_USERNAME,
    settings.PORTAINER_PASSWORD
)
http_client = HttpClient(60.0, read=60.0)
