from fastapi import HTTPException
from starlette import status


class PortainerAuthFailed(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication in Portainer failed! Invalid login or password"
        )


class PortainerUnauthorized(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Portainer token."
        )


class NotFound(HTTPException):
    def __init__(self, detail):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class DockerhubAuthFailed(HTTPException):
    def __init__(self, detail):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class ImageNotPulled(HTTPException):
    def __init__(self, detail: str | None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image not pulled. {detail}"
        )


class ContainerNotCreated(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Container not created"
        )


class ContainerNotStarted(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Container not started"
        )
