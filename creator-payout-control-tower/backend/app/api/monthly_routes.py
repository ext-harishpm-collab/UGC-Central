from pathlib import Path
import io,json,tempfile,shutil,zipfile
from fastapi import APIRouter,UploadFile,File,HTTPException
from fastapi.responses import StreamingResponse
from ..services.dual_dump_service import process_two_dumps,csv_bytes
from ..db.session import SessionLocal
from ..models import Earning,QCResult
router=APIRouter()

@router.post("/monthly/process-two-dumps")
def process_two_dumps_route(incentive_dump:UploadFile=File(...),revenue_share_dump:UploadFile=File(...),period:str=""):
    if not period:return HTTPException(400,"period is required")
    paths=[]
    try:
        for f in (incentive_dump,revenue_share_dump):
            if not (f.filename or "").lower().endswith((".xlsx",".xlsm")):raise HTTPException(400,"Only XLSX/XLSM files are supported")
            with tempfile.NamedTemporaryFile(suffix=Path(f.filename or "").suffix,delete=False) as tmp:
                shutil.copyfileobj(f.file,tmp);paths.append(tmp.name)
        return process_two_dumps(paths[0],paths[1],period)
    finally:
        for p in paths:Path(p).unlink(missing_ok=True)

@router.get("/monthly/author-level/export")
def author_level_export(period:str):
    db=SessionLocal()
    try:
        rows=db.query(Earning).filter(Earning.payment_period==period).all()
        grouped={}
        for e in rows:
            if not e.author_id:continue
            g=grouped.setdefault(e.author_id,{"inc":0.0,"rs":0.0,"gross":0.0,"count":0,"refs":[],"qc":set(),"types":set()})
            included=e.exclusion_reason is None
            if included:
                if e.reward_type=="INCENTIVE":g["inc"]+=float(e.gross or 0)
                if e.reward_type=="REVENUE_SHARE":g["rs"]+=float(e.gross or 0)
                g["gross"]+=float(e.gross or 0)
            g["count"]+=1;g["types"].add(e.content_type or "UNKNOWN");g["refs"].append(f"{e.source_file}:{e.source_sheet}:R{e.source_row}")
        qc= db.query(QCResult).filter(QCResult.period==period).all()
        by_entity={q.entity_id for q in qc}
        out=[]
        for aid,g in grouped.items():
            out.append({"Payment Period":period,"Author ID":aid,"Incentive Gross":g["inc"],"Gross Revenue Share":g["rs"],"Other Earnings":0,
                        "Gross Payable":g["gross"],"Recovery Applied":0,"Manual Adjustment":0,"TDS Amount":"",
                        "Final Net Payable":"","Content Type":" / ".join(sorted(g["types"])),"QC Status":"REVIEW" if by_entity else "SOURCE_QC_APPLIED",
                        "QC Findings":"See QC_Results.csv","Source References":" | ".join(g["refs"])})
        headers=["Payment Period","Author ID","Incentive Gross","Gross Revenue Share","Other Earnings","Gross Payable","Recovery Applied","Manual Adjustment","TDS Amount","Final Net Payable","Content Type","QC Status","QC Findings","Source References"]
        return StreamingResponse(io.BytesIO(csv_bytes(out,headers)),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="Author_Level_{period.replace(" ","_")}.csv"'})
    finally:db.close()

@router.get("/monthly/qc/export")
def qc_export(period:str):
    db=SessionLocal()
    try:
        rows=db.query(QCResult).filter(QCResult.period==period).all()
        out=[{"Period":r.period,"Entity":r.entity_id,"Rule ID":r.rule_id,"Severity":r.severity,"Message":r.message,"Detected":r.detected_value,"Expected":r.expected_value,"Status":r.status} for r in rows]
        headers=["Period","Entity","Rule ID","Severity","Message","Detected","Expected","Status"]
        return StreamingResponse(io.BytesIO(csv_bytes(out,headers)),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="QC_Results_{period.replace(" ","_")}.csv"'})
    finally:db.close()
