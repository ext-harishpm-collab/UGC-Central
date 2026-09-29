from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io
from ..services.final_export_service import export_frozen_batch
from ..services.parity_service import parity
router=APIRouter()
@router.get("/final/export/{batch_id}")
def final_export(batch_id:str):
    result=export_frozen_batch(batch_id)
    if not result.get("ok"):return result
    return StreamingResponse(io.BytesIO(result["csv"]),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="Final_Author_Level_{batch_id}.csv"'})
@router.get("/parity/{period}")
def period_parity(period:str):return parity(period)
