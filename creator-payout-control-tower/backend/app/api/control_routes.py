from fastapi import APIRouter
from ..services.control_report_service import control_report
router=APIRouter()
@router.get("/control/report/{period}")
def report(period:str):
    return control_report(period)
