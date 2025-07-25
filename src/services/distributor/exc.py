from src.core.exc import ClientError


class BotNotFound(ClientError):
    def __init__(self, bot_token: str):
        super().__init__(detail=f"Bot {bot_token} not found")
