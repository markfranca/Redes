import random as rnd
from app.models.models import SpeedTestResult

class SpeedTestController: 

    def get_speed_test_result(self) -> SpeedTestResult:
        download = f"{rnd.randint(50, 150)} Mbps"
        upload = f"{rnd.randint(10, 50)} Mbps"
        ping = f"{rnd.randint(10, 30)} ms"
        return SpeedTestResult(download=download, upload=upload, ping=ping)
    