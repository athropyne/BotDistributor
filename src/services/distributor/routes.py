from fastapi import APIRouter, Depends
from starlette import status

from src.core.security import TokenManager
from src.services.distributor.dto.input import INPUT_NewBotParams
from src.services.distributor.dto.output import OUTPUT_NewBotCreated
from src.services.distributor.service import SERVICE_DeployNewBot

distributor_router = APIRouter(prefix="/distributor", tags=["Distribution"])


@distributor_router.post(
    "/",
    summary="Deploy a new bot",
    description="""
        Launches a new Telegram bot with the parameters specified by the user.
        All 5xx errors returned are related to the server side. 
        You cannot fix them on the client side!
    """,
    status_code=status.HTTP_201_CREATED,
    response_model=OUTPUT_NewBotCreated,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail":
                            [
                                'Head \"https://registry-1.docker.io/v2/athropyne/telegram-bot/manifests/latest\": unauthorized: incorrect username or password',
                                "Authentication in Portainer failed! Invalid login or password",
                                "Invalid Portainer token",
                                "Image not pulled. <detail>",
                                "Container not created",
                                "Container not started",
                                "..."
                            ]}
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication error",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid access token"}
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Client error",
            "content": {
                "application/json": {
                    "example": {"detail": "Bot <bot_token> not found"}
                }
            }
        },
    },
    dependencies=[Depends(TokenManager.decode)]
)
async def deploy_new_bot(
        model: INPUT_NewBotParams,
        service: SERVICE_DeployNewBot = Depends()
):
    return await service(model)
