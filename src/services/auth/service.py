from fastapi import Depends

from src.core.config import settings
from src.core.interfaces import BaseService
from src.core.security import TokenManager
from src.services.auth.dto.input import INPUT_AuthData
from src.services.auth.dto.output import OUTPUT_TokenModel
from src.services.auth.exc import InvalidLoginOrPassword


class SERVICE_Auth(BaseService):
    def __init__(self):
        super().__init__()

    async def __call__(self, model: INPUT_AuthData):
        login = settings.ADMIN_PANEL_USERNAME
        password = settings.ADMIN_PANEL_PASSWORD
        if model.login != login or password != model.password:
            raise InvalidLoginOrPassword
        access_token = TokenManager.create(None)
        return OUTPUT_TokenModel(
            access_token=access_token
        )
