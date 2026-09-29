from pathlib import Path
from fastapi import APIRouter,UploadFile,File,HTTPException
from pydantic import BaseModel
from ..services.status import normalize_payment_status
from ..services.import_service import import_uploaded_workbook,list_imports
from ..imports.inspector import inspect_workbook
from ..services.master_service import master_summary
from ..services.ledger_service import list_ledger,ledger_summary
from ..services.rules_service import get_rules,save_rule
from ..services.calculation_service import calculate
from ..services.qc_service import run_qc
from ..services.reconciliation_service import reconcile
from ..services.uwt_import_service import import_uwt_workbook,fixed_uwt_rows
from ..services.uwt_export_service import build_uwt_workbook
from ..services.month_service import month_breakdown
from ..services.historical_service import backfill_files
from ..services.earning_service import ingest_earnings
from ..services.payout_service import build_preview
from ..services.batch_service import create_draft_batch,list_batches,freeze_batch
from ..services.entity_service import author_360,content_360
from ..services.recovery_service import ingest_recovery_and_adjustments
from ..services.tds_service import normalize_pan_status,effective_tds_rate
from fastapi.responses import StreamingResponse
import tempfile,shutil

router=APIRouter()
class RulePayload(BaseModel):
    rule_key:str
    value:float|None=None
    effective_from:str|None=None
    effective_to:str|None=None
    reason:str|None=None
    approved_by:str|None=None
class CalcPayload(BaseModel):
    incentive:float=0; revenue_share:float=0; other:float=0; marketing:float=0; platform:float=0; cop:float=0; flat:float=0; recovery:float=0; adjustment:float=0; tds_rate:float=0
class QCInput(BaseModel):
    author_id:str|None=None; content_type:str|None=None; incentive:float=0; contract_rs:float|None=None; product_rs:float|None=None; bank_ok:bool=False; pan_ok:bool=False; previously_paid:bool=False; recovery_double:bool=False; adjustment_reason:bool=True; payment_threshold:float=100; final_net:float=0

@router.get("/health")
def health(): return {"status":"ok","phase":14}
@router.get("/status/normalize/{raw_status}")
def status(raw_status:str): return {"input":raw_status,"normalized":normalize_payment_status(raw_status).value}
@router.get("/config/rules")
def rules(period:str|None=None): return get_rules(period)
@router.post("/config/rules")
def create_rule(p:RulePayload):
    try:return save_rule(p.rule_key,p.value or 0,p.effective_from,p.effective_to,p.reason,p.approved_by)
    except ValueError as e:raise HTTPException(400,str(e))
@router.get("/imports")
def imports():return list_imports()
@router.post("/import/upload")
def import_upload(file:UploadFile=File(...)):return import_uploaded_workbook(file)
@router.post("/historical/earnings")
def historical_earnings(file:UploadFile=File(...),period:str|None=None):
    with tempfile.NamedTemporaryFile(suffix=Path(file.filename or "").suffix,delete=False) as tmp:shutil.copyfileobj(file.file,tmp);path=tmp.name
    try:return ingest_earnings(path,period)
    finally:Path(path).unlink(missing_ok=True)
@router.post("/historical/recovery-adjustment")
def historical_recovery(file:UploadFile=File(...),period:str):
    with tempfile.NamedTemporaryFile(suffix=Path(file.filename or "").suffix,delete=False) as tmp:shutil.copyfileobj(file.file,tmp);path=tmp.name
    try:return ingest_recovery_and_adjustments(path,period)
    finally:Path(path).unlink(missing_ok=True)
@router.post("/uwt/import")
def uwt_import(file:UploadFile=File(...)):
    with tempfile.NamedTemporaryFile(suffix=Path(file.filename or "").suffix,delete=False) as tmp:shutil.copyfileobj(file.file,tmp);path=tmp.name
    try:return import_uwt_workbook(path)
    finally:Path(path).unlink(missing_ok=True)
@router.get("/uwt/rows")
def uwt_rows(period:str|None=None,status:str|None=None):return fixed_uwt_rows(period,status)
@router.get("/uwt/export")
def uwt_export(period:str|None=None,status:str|None=None):
    return StreamingResponse(build_uwt_workbook(period,status),media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":"attachment; filename=uwt_final.xlsx"})
@router.get("/payout/preview")
def payout_preview(period:str,marketing_cap:float|None=None,cop_cap:float|None=None,cap_mode:str="INDIVIDUAL",tds_rate:float=0):return build_preview(period,marketing_cap,cop_cap,cap_mode,tds_rate)
@router.post("/payout/batch")
def payout_batch(period:str,marketing_cap:float|None=None,cop_cap:float|None=None,cap_mode:str="INDIVIDUAL",tds_rate:float=0):return create_draft_batch(period,marketing_cap,cop_cap,cap_mode,tds_rate)
@router.get("/payout/batches")
def batches(period:str|None=None):return list_batches(period)
@router.post("/payout/batch/{batch_id}/freeze")
def batch_freeze(batch_id:str):return freeze_batch(batch_id)
@router.get("/exceptions")
def exceptions(period:str|None=None):
    from ..services.exception_service import open_exceptions
    return open_exceptions(period)
@router.get("/author/{author_id}/360")
def author_view(author_id:str,period:str|None=None):return author_360(author_id,period)
@router.get("/content/{content_id}/360")
def content_view(content_id:str,period:str|None=None):return content_360(content_id,period)
@router.get("/master/summary")
def summary():return master_summary()
@router.get("/ledger")
def ledger_rows(month:str|None=None,content_type:str|None=None,status:str|None=None,show_id:str|None=None,book_id:str|None=None,author_id:str|None=None):return list_ledger(month,content_type,status,show_id,book_id,author_id)
@router.get("/ledger/summary")
def ledger_sum(month:str|None=None):return ledger_summary(month)
@router.get("/month/breakdown")
def breakdown(month:str|None=None):return month_breakdown(month)
@router.get("/tax/pan-status")
def pan_status(value:str):return {"normalized":normalize_pan_status(value)}
@router.get("/tax/rate")
def tax_rate(pan_status:str,standard_rate:float=0.10,invalid_rate:float=0.20):
    rate=effective_tds_rate(pan_status,standard_rate,invalid_rate)
    return {"pan_status":normalize_pan_status(pan_status),"tds_rate":float(rate) if rate is not None else None}
@router.post("/calculate")
def calc(payload:CalcPayload):return calculate(payload.model_dump())
@router.post("/qc/run")
def qc(payload:QCInput):return run_qc(payload.model_dump())
@router.post("/reconcile")
def recon(payload:dict):return reconcile(**payload)
