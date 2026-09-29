from fastapi import APIRouter
from ..services.validation_service import validate_month
router=APIRouter()
@router.get("/validation/month/{period}")
def validation_month(period:str):
    return validate_month(period)
