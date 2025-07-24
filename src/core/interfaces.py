from abc import abstractmethod


class BaseService:
    def __init__(self):
        super().__init__()

    @abstractmethod
    async def __call__(self, *args, **kwargs): ...
