from fastapi import APIRouter,UploadFile,File,HTTPException
from fastapi.responses import StreamingResponse
from ..services.dual_dump_service import process_two_dumps,csv_bytes
import tempfile,shutil,zipfile,io

router=APIRouter()

@router.post("/monthly/process-two-dumps")
def monthly_process_two_dumps(incentive_dump:UploadFile=File(...), revenue_share_dump:UploadFile=File(...), period:str=""):
    if not period: raise HTTPException(400,"period is required")
    paths=[]
    try:
        for f in [incentive_dump,revenue_share_dump]:
            if not (f.filename or "").lower().endswith((".xlsx",".xlsm")): raise HTTPException(400,"XLSX/XLSM only")
            with tempfile.NamedTemporaryFile(suffix=".xlsx",delete=False) as tmp:
                shutil.copyfileobj(f.file,tmp);paths.append(tmp.name)
        result=process_two_dumps(paths[0],paths[1],period)
        return result
    finally:
        for p in paths:
            import os
            try:os.unlink(p)
            except OSError:pass

@router.post("/monthly/export-qc-pack")
def monthly_export_qc_pack(incentive_dump:UploadFile=File(...), revenue_share_dump:UploadFile=File(...), period:str=""):
    if not period: raise HTTPException(400,"period is required")
    paths=[]
    try:
        for f in [incentive_dump,revenue_share_dump]:
            with tempfile.NamedTemporaryFile(suffix=".xlsx",delete=False) as tmp:shutil.copyfileobj(f.file,tmp);paths.append(tmp.name)
        result=process_two_dumps(paths[0],paths[1],period)
        author_h=["period","author_id","incentive_gross","revenue_share_gross","gross","source_row_count","source_refs"]
        show_h=["period","author_id","book_id","show_id","incentive_gross","revenue_share_gross","gross","source_row_count","sources"]
        qc_h=["severity","rule_id","message","author_id","book_id","show_id","source_sheet","source_row"]
        z=io.BytesIO()
        with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as q:
            q.writestr("Author_Level.csv",csv_bytes(result["author_level_rows"],author_h))
            q.writestr("Show_Level_Lineage.csv",csv_bytes(result["show_level_rows"],show_h))
            q.writestr("QC_Results.csv",csv_bytes(result["qc_rows"],qc_h))
            q.writestr("QC_Summary.json",__import__("json").dumps(result["qc_summary"],indent=2))
            q.writestr("Process_Summary.json",__import__("json").dumps(result["input_summary"],indent=2))
        z.seek(0)
        return StreamingResponse(z,media_type="application/zip",headers={"Content-Disposition":f'attachment; filename="payout_qc_pack_{period.replace(" ","_")}.zip"'})
    finally:
        for p in paths:
            import os
            try:os.unlink(p)
            except OSError:pass
