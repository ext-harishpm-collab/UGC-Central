from pathlib import Path
import io,tempfile,shutil,csv,json
from fastapi import APIRouter,UploadFile,File,HTTPException
from fastapi.responses import StreamingResponse
from ..services.dual_dump_service import process_two_dumps,csv_bytes
from ..db.session import SessionLocal
from ..models import Earning,QCResult,RawImportRow,RuleConfig,MonthlyRun

router=APIRouter()

def _temp(upload):
    with tempfile.NamedTemporaryFile(suffix=Path(upload.filename or "").suffix,delete=False) as tmp:
        shutil.copyfileobj(upload.file,tmp)
        return tmp.name

@router.post("/monthly/process-two-dumps")
def process_two_dumps_route(incentive_dump:UploadFile=File(...),revenue_share_dump:UploadFile=File(...),period:str=""):
    if not period: raise HTTPException(400,"period is required")
    p1=p2=None
    try:
        p1=_temp(incentive_dump); p2=_temp(revenue_share_dump)
        return process_two_dumps(p1,p2,period)
    finally:
        for p in (p1,p2):
            if p: Path(p).unlink(missing_ok=True)

def _mapping_key(period, stream, field):
    return "monthly_mapping::{}::{}::{}".format(period, stream, field)


@router.get("/monthly/column-options")
def column_options(period: str):
    db=SessionLocal()
    try:
        runs=db.query(MonthlyRun).filter(MonthlyRun.period==period).all()
        batch_ids=[x.id for x in runs]
        rows=db.query(RawImportRow).filter(RawImportRow.batch_id.in_(batch_ids)).all() if batch_ids else []
        options={"INCENTIVE_DUMP":[],"REVENUE_SHARE_DUMP":[],"TDS_FACTOR":[]}
        seen={k:set() for k in options}
        for row in rows:
            try: payload=json.loads(row.payload or "{}")
            except Exception: payload={}
            stream=row.sheet_kind
            if stream not in {"INCENTIVE_DUMP","REVENUE_SHARE_DUMP"}:
                continue
            for key in payload:
                if key and key not in seen[stream]:
                    seen[stream].add(key)
                    options[stream].append(key)
                if key and "tds" in key.lower() and key not in seen["TDS_FACTOR"]:
                    seen["TDS_FACTOR"].add(key)
                    options["TDS_FACTOR"].append(key)
        for key in options:
            options[key].sort()
        return options
    finally:
        db.close()


@router.get("/monthly/column-mapping")
def get_column_mapping(period: str):
    db=SessionLocal()
    try:
        rows=db.query(RuleConfig).filter(RuleConfig.scope_type=="MONTHLY_COLUMN_MAPPING").all()
        wanted={row.rule_key:row.value_text or "" for row in rows if row.rule_key.startswith("monthly_mapping::{}::".format(period))}
        return {
            "inc_gross":wanted.get(_mapping_key(period,"INCENTIVE_DUMP","gross"),""),
            "rs_gross":wanted.get(_mapping_key(period,"REVENUE_SHARE_DUMP","gross"),""),
            "tds_factor":wanted.get(_mapping_key(period,"ALL","tds_factor"),"")
        }
    finally:
        db.close()


@router.post("/monthly/column-mapping")
def save_column_mapping(payload: dict):
    period=payload.get("period")
    if not period:
        raise HTTPException(400,"period is required")
    db=SessionLocal()
    try:
        fields={
            _mapping_key(period,"INCENTIVE_DUMP","gross"):payload.get("inc_gross",""),
            _mapping_key(period,"REVENUE_SHARE_DUMP","gross"):payload.get("rs_gross",""),
            _mapping_key(period,"ALL","tds_factor"):payload.get("tds_factor","")
        }
        for rule_key,value in fields.items():
            existing=db.query(RuleConfig).filter(RuleConfig.rule_key==rule_key,RuleConfig.scope_type=="MONTHLY_COLUMN_MAPPING").first()
            if existing:
                existing.value_text=str(value or "")
            else:
                db.add(RuleConfig(id=__import__("uuid").uuid4().hex,rule_key=rule_key,scope_type="MONTHLY_COLUMN_MAPPING",value_text=str(value or ""),reason="Monthly calculation source mapping"))
        db.commit()
        return {"saved":True,**payload}
    finally:
        db.close()


@router.get("/monthly/author-level/export")
def author_level_export(period:str):
    db=SessionLocal()
    try:
        rows=db.query(Earning).filter(Earning.payment_period==period).all()
        grouped={}
        for e in rows:
            if not e.author_id: continue
            g=grouped.setdefault(e.author_id,{"inc":0.0,"rs":0.0,"gross":0.0,"count":0,"refs":[],"types":set(),"excluded":0})
            g["count"]+=1
            g["refs"].append(f"{e.source_file}:{e.source_sheet}:R{e.source_row}")
            g["types"].add(e.content_type or "UNKNOWN")
            if e.exclusion_reason:
                g["excluded"]+=1
                continue
            amount=float(e.gross or 0)
            if e.reward_type=="INCENTIVE": g["inc"]+=amount
            elif e.reward_type=="REVENUE_SHARE": g["rs"]+=amount
            g["gross"]+=amount
        qrows=db.query(QCResult).filter(QCResult.period==period).all()
        qcount=len(qrows)
        out=[]
        for aid,g in grouped.items():
            out.append({
                "Payment Period":period,"Author ID":aid,"Incentive Gross":g["inc"],
                "Gross Revenue Share":g["rs"],"Other Earnings":0,"Gross Payable":g["gross"],
                "Recovery Applied":"","Manual Adjustment":"","TDS %":"","TDS Amount":"","Final Net Payable":"",
                "Content Type":" / ".join(sorted(g["types"])),"Excluded Source Rows":g["excluded"],
                "QC Status":"SOURCE_QC_APPLIED" if qcount==0 else "QC_REVIEW",
                "QC Findings Count":qcount,"Source References":" | ".join(g["refs"])
            })
        headers=list(out[0].keys()) if out else ["Payment Period","Author ID","Incentive Gross","Gross Revenue Share","Other Earnings","Gross Payable","Recovery Applied","Manual Adjustment","TDS %","TDS Amount","Final Net Payable","Content Type","Excluded Source Rows","QC Status","QC Findings Count","Source References"]
        return StreamingResponse(io.BytesIO(csv_bytes(out,headers)),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="Author_Level_{period.replace(" ","_")}.csv"'})
    finally: db.close()

@router.get("/monthly/qc/export")
def qc_export(period:str):
    db=SessionLocal()
    try:
        rows=db.query(QCResult).filter(QCResult.period==period).all()
        out=[{"Period":r.period,"Entity":r.entity_id,"Rule ID":r.rule_id,"Severity":r.severity,"Message":r.message,"Detected":r.detected_value,"Expected":r.expected_value,"Status":r.status} for r in rows]
        headers=["Period","Entity","Rule ID","Severity","Message","Detected","Expected","Status"]
        return StreamingResponse(io.BytesIO(csv_bytes(out,headers)),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="QC_Results_{period.replace(" ","_")}.csv"'})
    finally: db.close()

@router.get("/monthly/source-lines")
def source_lines(period:str):
    db=SessionLocal()
    try:
        rows=db.query(Earning).filter(Earning.payment_period==period).order_by(Earning.source_file,Earning.source_sheet,Earning.source_row).all()
        out=[]
        for e in rows:
            out.append({"Period":e.payment_period,"Author ID":e.author_id,"Book ID":e.book_id,"Show ID":e.show_id,"Content Type":e.content_type,
                        "Reward Type":e.reward_type,"Pay Flag":e.pay_flag,"Excluded":e.exclusion_reason or "",
                        "Gross":float(e.gross or 0),"TDS":float(e.tds or 0),"Net":float(e.net or 0),
                        "Source File":e.source_file,"Source Sheet":e.source_sheet,"Source Row":e.source_row})
        return out
    finally: db.close()
