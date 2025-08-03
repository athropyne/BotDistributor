from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.services.auth.routes import auth_router
from src.services.distributor.routes import distributor_router


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(auth_router)
app.include_router(distributor_router)
