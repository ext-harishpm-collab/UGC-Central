from fastapi import APIRouter
from ..services.parity_service import parity
router=APIRouter()
@router.get("/parity/{period}")
def parity_endpoint(period:str):
    return parity(period)
