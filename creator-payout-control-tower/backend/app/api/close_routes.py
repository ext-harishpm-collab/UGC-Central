from fastapi import APIRouter
from ..services.close_report_service import close_report
router=APIRouter()
@router.get("/cycle/close-report")
def cycle_close_report(period:str):return close_report(period)
