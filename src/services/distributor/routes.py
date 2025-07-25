from fastapi import APIRouter, Depends
from starlette import status

from src.services.distributor.dto.input import INPUT_NewBotParams
from src.services.distributor.dto.output import OUTPUT_NewBotCreated
from src.services.distributor.service import SERVICE_DeployNewBot

distributor_router = APIRouter(prefix="/distributor", tags=["Distribution"])


@distributor_router.post(
    "/",
    summary="Deploy a new bot",
    description="""
        Launches a new Telegram bot with the parameters specified by the user.
        All returned errors are related to the server side. 
        You cannot fix them on the client side! 
        4xx error codes are only used to better understand what happened.
    """,
    status_code=status.HTTP_201_CREATED,
    response_model=OUTPUT_NewBotCreated,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Head \"https://registry-1.docker.io/v2/athropyne/telegram-bot/manifests/latest\": unauthorized: incorrect username or password"}
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Resource not found. Returns if an incorrect PORTAINER_URL is specified or the ID of the Portainer virtual environment is incorrectly specified or calculated",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Unable to find an environment with the specified identifier inside the database"}
                }
            }
        },

        status.HTTP_401_UNAUTHORIZED: {
            "description": "Ошибка аутентификации в Portainer. Возвращается если сервер не смог самостоятельно аутентифицироваться  в Portainer ",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid Portainer token."}
                }
            }
        }
    }
)
async def deploy_new_bot(
        model: INPUT_NewBotParams,
        service: SERVICE_DeployNewBot = Depends()
):
    return await service(model)
