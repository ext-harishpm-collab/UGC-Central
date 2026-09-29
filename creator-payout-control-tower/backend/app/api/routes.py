from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.status import normalize_payment_status
from ..services.import_service import import_uploaded_workbook, list_imports
from ..imports.inspector import inspect_workbook

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "service": "creator-payout-control-tower", "phase": 2}

@router.get("/status/normalize/{raw_status}")
def normalize(raw_status: str):
    return {"input": raw_status, "normalized": normalize_payment_status(raw_status).value}

@router.get("/config/rule-keys")
def rule_keys():
    return {"configurable": ["MARKETING_CAP", "COP_CAP", "PLATFORM_RATE", "FLAT_DEDUCTION_RATE", "PAYMENT_THRESHOLD"]}

@router.get("/imports")
def imports():
    return list_imports()

@router.post("/import/inspect")
def import_inspect(file: UploadFile = File(...)):
    name = file.filename or ""
    if not name.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Only XLSX/XLSM files are supported.")
    import tempfile, shutil
    suffix = Path(name).suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        path = tmp.name
    return inspect_workbook(path)

@router.post("/import/upload")
def import_upload(file: UploadFile = File(...)):
    name = file.filename or ""
    if not name.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Only XLSX/XLSM files are supported.")
    try:
        return import_uploaded_workbook(file)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Import failed: {exc}")
