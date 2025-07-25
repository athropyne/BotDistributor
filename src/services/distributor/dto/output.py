from pydantic import BaseModel, Field


class OUTPUT_NewBotCreated(BaseModel):
    message: str = Field("Bot created and running", description="Successful message")
    container_name: str = Field(..., description="Container name")
    container_id: str = Field(..., description="ID of the created container with a new instance of the telegram bot")
