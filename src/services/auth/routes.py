from fastapi import APIRouter, Depends
from starlette import status

from src.core import utils
from src.services.auth.dto.input import INPUT_AuthData
from src.services.auth.dto.output import OUTPUT_TokenModel
from src.services.auth.service import SERVICE_Auth

auth_router = APIRouter(prefix="/auth", tags=["Безопасность"])


@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Authenticate",
    description="""
        Returns the access token
    """,
    response_model=OUTPUT_TokenModel,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to create an access token due to a server error"}
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Authentication error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid login or password"}
                }
            }
        },
    }
)
async def auth(
        model: INPUT_AuthData = Depends(utils.convert_auth_data),
        service: SERVICE_Auth = Depends()
):
    return await service(model)
