from pydantic import BaseModel

class SpeedTestResult(BaseModel):
    download: str
    upload: str
    ping: str