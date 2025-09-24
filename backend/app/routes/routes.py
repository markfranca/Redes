

from fastapi import APIRouter
from ..controllers.controllers import SpeedTestController
from ..models.models import SpeedTestResult

router = APIRouter()

@router.get("/speedtest", response_model=SpeedTestResult)
def get_speed_test():
    controller = SpeedTestController()
    return controller.get_speed_test_result()
