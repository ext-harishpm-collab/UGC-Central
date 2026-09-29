import json,uuid
from pathlib import Path
from fastapi import UploadFile
from ..db.session import SessionLocal
from ..models import ImportBatch,RawImportRow,PaymentTransaction
from ..imports.pipeline import ingest_workbook

def save_upload(upload:UploadFile,root="./uploads")->str:
    Path(root).mkdir(parents=True,exist_ok=True)
    path=Path(root)/f"{uuid.uuid4().hex}_{upload.filename}"
    with open(path,"wb") as f:
        while chunk:=upload.file.read(1024*1024):f.write(chunk)
    return str(path)

def import_uploaded_workbook(upload:UploadFile)->dict:
    path=save_upload(upload);data=ingest_workbook(path);db=SessionLocal()
    try:
        existing=db.query(ImportBatch).filter(ImportBatch.checksum==data["batch_id"]).first()
        if existing:return {"duplicate":True,"batch_id":existing.id,"filename":existing.filename}
        db.add(ImportBatch(id=data["batch_id"],filename=data["filename"],payment_period=data["inferred_period"],checksum=data["batch_id"],
                           total_rows=data["total_rows"],payment_event_rows=data["payment_event_rows"],status="IMPORTED"))
        for e in data["payment_events"]:
            rid=str(uuid.uuid5(uuid.NAMESPACE_URL,f'{data["batch_id"]}:{e["source_sheet"]}:{e["source_row"]}'))
            db.add(RawImportRow(id=rid,batch_id=data["batch_id"],source_sheet=e["source_sheet"],source_row=e["source_row"],
                                sheet_kind=e["kind"],payload=json.dumps(e["raw"],ensure_ascii=False)))
            db.add(PaymentTransaction(
                id=rid,author_id=e.get("author_id"),book_id=e.get("book_id"),show_id=e.get("show_id"),payment_type=e.get("kind"),
                amount_before_tax=e.get("amount_before_tax"),amount_after_tax=e.get("amount_after_tax"),currency="INR",
                status=e.get("status","UNMATCHED"),utr=e.get("utr"),payout_id=e.get("payout_id"),original_status=e.get("status_raw"),
                source_file=e.get("source_file"),source_sheet=e.get("source_sheet"),source_row=e.get("source_row"),
                payment_period=data["inferred_period"],content_type=None,
                ledger_state="CLOSED" if e.get("status")=="SUCCESS" else "RETRYABLE" if e.get("status") in {"FAILED","REVERSED"} else "OPEN",
                account_number=e.get("account_number"),ifsc=e.get("ifsc"),bank_name=e.get("bank_name")
            ))
        db.commit()
        return {"duplicate":False,"batch_id":data["batch_id"],"filename":data["filename"],"payment_period":data["inferred_period"],
                "total_rows":data["total_rows"],"payment_event_rows":data["payment_event_rows"],"sheets":data["sheets"]}
    except Exception:db.rollback();raise
    finally:db.close()
def list_imports():
    db=SessionLocal()
    try:return [{"batch_id":b.id,"filename":b.filename,"payment_period":b.payment_period,"status":b.status,"total_rows":b.total_rows,
                 "payment_event_rows":b.payment_event_rows,"imported_at":b.imported_at.isoformat()} for b in db.query(ImportBatch).order_by(ImportBatch.imported_at.desc()).all()]
    finally:db.close()
