from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    time: str
    api_version: str
    app_name: str
    description: str
    python_version: str
    os: str
    os_version: str
    server: str
    author: str
    env: str
