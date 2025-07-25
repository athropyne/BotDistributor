from fastapi import HTTPException
from starlette import status


class InternalError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class PortainerAuthFailed(InternalError):
    def __init__(self):
        super().__init__(
            detail="Authentication in Portainer failed! Invalid login or password"
        )


class PortainerUnauthorized(InternalError):
    def __init__(self):
        super().__init__(
            detail="Invalid Portainer token"
        )


class InvalidURL(InternalError):
    def __init__(self, detail):
        super().__init__(
            detail=detail
        )


class DockerhubAuthFailed(InternalError):
    def __init__(self, detail):
        super().__init__(
            detail=detail
        )


class ImageNotPulled(InternalError):
    def __init__(self, detail: str | None):
        super().__init__(
            detail=f"Image not pulled. {detail}"
        )


class ContainerNotCreated(InternalError):
    def __init__(self):
        super().__init__(
            detail="Container not created"
        )


class ContainerNotStarted(InternalError):
    def __init__(self):
        super().__init__(
            detail="Container not started"
        )


class ClientError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotAuthorized(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ExpiredSignatureError(NotAuthorized):
    def __init__(self):
        super().__init__(detail="Token signature error")


class InvalidTokenError(NotAuthorized):
    def __init__(self):
        super().__init__(detail="Invalid access token")
