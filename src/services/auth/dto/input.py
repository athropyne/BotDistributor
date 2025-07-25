from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class INPUT_AuthData(BaseModel):
    login: str = Field(..., max_length=30)
    password: str = Field(..., max_length=100)


class INPUT_VerifyEmail(BaseModel):
    email: EmailStr
    verification_code: UUID
