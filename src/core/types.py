from pydantic import BaseModel

ID = int


class IDModel(BaseModel):
    id: ID
