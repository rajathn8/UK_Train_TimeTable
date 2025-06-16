"""
Custom exceptions for the health module
"""
from fastapi import HTTPException


class HealthCheckException(HTTPException):
    def __init__(self):
        super().__init__(status_code=500, detail="Raj Service Failure - contact rajath rao")
