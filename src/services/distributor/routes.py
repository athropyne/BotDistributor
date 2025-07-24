from fastapi import APIRouter
from starlette import status

from src.services.distributor.dto.input import INPUT_NewBotParams

distributor_router = APIRouter(prefix="/distributor", tags=["Distribution"])

@distributor_router.post(
    "/",
    summary="Deploy a new bot",
    description="Launches a new Telegram bot with the parameters specified by the user.",
    status_code=status.HTTP_201_CREATED
)
async def deploy_new_bot(
        model: INPUT_NewBotParams,
        service: SERVICE_DeployNewBot
):
    return await service(model)