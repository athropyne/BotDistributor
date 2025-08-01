from pydantic import BaseModel, Field


class INPUT_NewBotParams(BaseModel):
    bot_token: str = Field(..., description="Your bot token")
    bot_title: str = Field(..., description="Your bot title")
    bot_username: str = Field(..., description="Your bot username")
    creator_id: int = Field(..., description="Creator user id")
    bot_link: str = Field(..., description="Bot lint")
