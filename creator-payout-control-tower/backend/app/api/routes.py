from pathlib import Path
from fastapi import APIRouter,UploadFile,File,HTTPException
from pydantic import BaseModel
from ..services.status import normalize_payment_status
from ..services.import_service import import_uploaded_workbook,list_imports
from ..imports.inspector import inspect_workbook
from ..services.master_service import enrich_from_payment_events,master_summary
from ..services.ledger_service import list_ledger,ledger_summary
from ..services.rules_service import get_rules,save_rule
from ..services.calculation_service import calculate
from ..services.qc_service import run_qc
from ..services.reconciliation_service import reconcile

router=APIRouter()
class RulePayload(BaseModel): rule_key:str; value:float; effective_from:str|None=None; effective_to:str|None=None; reason:str|None=None; approved_by:str|None=None
class CalcPayload(BaseModel):
    incentive:float=0; revenue_share:float=0; other:float=0; marketing:float=0; platform:float=0; cop:float=0; flat:float=0; recovery:float=0; adjustment:float=0; tds_rate:float=0
class QCInput(BaseModel):
    author_id:str|None=None; content_type:str|None=None; incentive:float=0; contract_rs:float|None=None; product_rs:float|None=None; bank_ok:bool=False; pan_ok:bool=False; previously_paid:bool=False; recovery_double:bool=False; adjustment_reason:bool=True; payment_threshold:float=100; final_net:float=0
class ReconInput(BaseModel):
    payout_id:str|None=None; utr:str|None=None; author_id:str|None=None; book_id:str|None=None; amount:float|None=None; raw_status:str|None=None

@router.get("/health")
def health(): return {"status":"ok","phase":4}
@router.get("/status/normalize/{raw_status}")
def status(raw_status:str): return {"input":raw_status,"normalized":normalize_payment_status(raw_status).value}
@router.get("/config/rules")
def rules(period:str|None=None): return get_rules(period)
@router.post("/config/rules")
def create_rule(p:RulePayload):
    try:return save_rule(p.rule_key,p.value,p.effective_from,p.effective_to,p.reason,p.approved_by)
    except ValueError as e: raise HTTPException(400,str(e))
@router.get("/imports")
def imports(): return list_imports()
@router.post("/import/inspect")
def inspect(file:UploadFile=File(...)):
    name=file.filename or ""
    if not name.lower().endswith((".xlsx",".xlsm")): raise HTTPException(400,"Only XLSX/XLSM are supported")
    import tempfile,shutil
    with tempfile.NamedTemporaryFile(suffix=Path(name).suffix,delete=False) as tmp: shutil.copyfileobj(file.file,tmp); path=tmp.name
    try:return inspect_workbook(path)
    finally:Path(path).unlink(missing_ok=True)
@router.post("/import/upload")
def upload(file:UploadFile=File(...)):
    name=file.filename or ""
    if not name.lower().endswith((".xlsx",".xlsm")): raise HTTPException(400,"Only XLSX/XLSM are supported")
    try:return import_uploaded_workbook(file)
    except Exception as e: raise HTTPException(500,f"Import failed: {e}")
@router.post("/master/enrich")
def master_enrich(): return enrich_from_payment_events()
@router.get("/master/summary")
def summary(): return master_summary()
@router.get("/ledger/summary")
def ledger_sum(month:str|None=None): return ledger_summary(month)
@router.get("/ledger")
def ledger_rows(month:str|None=None,content_type:str|None=None,status:str|None=None,show_id:str|None=None,book_id:str|None=None,author_id:str|None=None): return list_ledger(month,content_type,status,show_id,book_id,author_id)
@router.post("/calculate")
def calculate_endpoint(p:CalcPayload): return calculate(p.model_dump())
@router.post("/qc/run")
def qc_endpoint(p:QCInput): return run_qc(p.model_dump())
@router.post("/reconcile")
def reconcile_endpoint(p:ReconInput): return reconcile(**p.model_dump())
