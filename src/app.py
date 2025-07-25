from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.exc import PortainerAuthFailed
from src.core.infrastructures import portainer
from src.services.distributor.routes import distributor_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await portainer.auth()
        if settings.PORTAINER_ENDPOINT_ID is None:
            await portainer.get_environment_id({"Authorization": f"Bearer {portainer.access_token}"})
        else:
            portainer.environment_id = settings.PORTAINER_ENDPOINT_ID
    except (httpx.ConnectError, httpx.InvalidURL) as e:
        logger.error("Invalid Portainer URL")
        raise RuntimeError("Portainer is not available. Invalid Portainer URL")
    except PortainerAuthFailed as e:
        logger.error(e.detail)
        raise
    logger.info(f"Server started {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    yield
    logger.info("Server stopped")


app = FastAPI(
    lifespan=lifespan,
    title="Bot distributor"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(distributor_router)
