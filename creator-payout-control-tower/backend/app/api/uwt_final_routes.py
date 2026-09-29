from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io,csv
from ..services.frozen_uwt_service import build_frozen_rows,UWT_COLUMNS
router=APIRouter()
@router.get("/final/uwt/{batch_id}")
def final_uwt(batch_id:str):
    result=build_frozen_rows(batch_id)
    if not result.get("ok"):return result
    b=io.StringIO();w=csv.DictWriter(b,fieldnames=UWT_COLUMNS);w.writeheader();w.writerows(result["rows"])
    return StreamingResponse(io.BytesIO(b.getvalue().encode("utf-8-sig")),media_type="text/csv",
        headers={"Content-Disposition":f'attachment; filename="UWT_Final_{batch_id}.csv"'})
