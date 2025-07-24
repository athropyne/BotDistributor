from fastapi import APIRouter, Depends
from starlette import status

from src.services.distributor.dto.input import INPUT_NewBotParams
from src.services.distributor.service import SERVICE_DeployNewBot

distributor_router = APIRouter(prefix="/distributor", tags=["Distribution"])


@distributor_router.post(
    "/",
    summary="Deploy a new bot",
    description="Launches a new Telegram bot with the parameters specified by the user.",
    status_code=status.HTTP_201_CREATED
)
async def deploy_new_bot(
        model: INPUT_NewBotParams,
        service: SERVICE_DeployNewBot = Depends()
):
    return await service(model)
