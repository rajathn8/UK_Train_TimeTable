from fastapi import HTTPException


class HealthCheckException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500, detail="Service failure occurred. Please contact support."
        )
