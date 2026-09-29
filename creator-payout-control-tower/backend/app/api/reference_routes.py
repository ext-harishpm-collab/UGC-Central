from pathlib import Path
from fastapi import APIRouter,UploadFile,File,HTTPException
from ..services.reference_service import import_reference_workbook,author_controls
router=APIRouter()

@router.post("/reference/{kind}/import")
def reference_import(kind:str,file:UploadFile=File(...)):
    if kind not in {"contract","pan","compliance"}:raise HTTPException(400,"kind must be contract, pan or compliance")
    import tempfile,shutil
    with tempfile.NamedTemporaryFile(suffix=Path(file.filename or "").suffix,delete=False) as tmp:shutil.copyfileobj(file.file,tmp);path=tmp.name
    try:return import_reference_workbook(path,kind)
    finally:Path(path).unlink(missing_ok=True)

@router.get("/reference/author/{author_id}")
def reference_author(author_id:str,period:str|None=None):return author_controls(author_id,period)
