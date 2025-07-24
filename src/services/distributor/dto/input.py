from pydantic import BaseModel, Field


class INPUT_NewBotParams(BaseModel):
    bot_token: str = Field(..., description="Your bot token")
