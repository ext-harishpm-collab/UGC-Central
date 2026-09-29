from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from ..services.status import normalize_payment_status
from ..services.import_service import import_uploaded_workbook, list_imports
from ..imports.inspector import inspect_workbook
from ..services.master_service import enrich_from_payment_events, master_summary
from ..services.ledger_service import list_ledger, ledger_summary
from ..services.rules_service import get_rules, save_rule

router=APIRouter()

class RulePayload(BaseModel):
    rule_key:str
    value:float
    effective_from:str|None=None
    effective_to:str|None=None
    reason:str|None=None
    approved_by:str|None=None

@router.get("/health")
def health():return {"status":"ok","service":"creator-payout-control-tower","phase":3}

@router.get("/status/normalize/{raw_status}")
def normalize(raw_status:str):return {"input":raw_status,"normalized":normalize_payment_status(raw_status).value}

@router.get("/config/rules")
def rules(period:str|None=None):return get_rules(period)

@router.post("/config/rules")
def create_rule(payload:RulePayload):
    try:return save_rule(payload.rule_key,payload.value,payload.effective_from,payload.effective_to,payload.reason,payload.approved_by)
    except ValueError as exc:raise HTTPException(status_code=400,detail=str(exc))

@router.get("/imports")
def imports():return list_imports()

@router.post("/import/inspect")
def import_inspect(file:UploadFile=File(...)):
    name=file.filename or ""
    if not name.lower().endswith((".xlsx",".xlsm")):raise HTTPException(status_code=400,detail="Only XLSX/XLSM are supported.")
    import tempfile,shutil
    with tempfile.NamedTemporaryFile(suffix=Path(name).suffix,delete=False) as tmp:
        shutil.copyfileobj(file.file,tmp);path=tmp.name
    try:return inspect_workbook(path)
    finally:Path(path).unlink(missing_ok=True)

@router.post("/import/upload")
def import_upload(file:UploadFile=File(...)):
    name=file.filename or ""
    if not name.lower().endswith((".xlsx",".xlsm")):raise HTTPException(status_code=400,detail="Only XLSX/XLSM are supported.")
    try:return import_uploaded_workbook(file)
    except Exception as exc:raise HTTPException(status_code=500,detail=f"Import failed: {exc}")

@router.post("/master/enrich")
def master_enrich():return enrich_from_payment_events()

@router.get("/master/summary")
def summary():return master_summary()

@router.get("/ledger/summary")
def ledger_sum(month:str|None=None):return ledger_summary(month)

@router.get("/ledger")
def ledger_rows(month:str|None=None,content_type:str|None=None,status:str|None=None,show_id:str|None=None,book_id:str|None=None,author_id:str|None=None):
    return list_ledger(month,content_type,status,show_id,book_id,author_id)
