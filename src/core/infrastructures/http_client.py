import httpx
from httpx._config import UnsetType, Timeout, UNSET


class HttpClient:
    def __init__(self,
                 timeout: float | None | tuple[
                     float | None, float | None, float | None, float | None] | Timeout | UnsetType = UNSET,
                 *,
                 connect: None | float | UnsetType = UNSET,
                 read: None | float | UnsetType = UNSET,
                 write: None | float | UnsetType = UNSET,
                 pool: None | float | UnsetType = UNSET):
        self.timeout = timeout

    async def __call__(self):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            yield client
