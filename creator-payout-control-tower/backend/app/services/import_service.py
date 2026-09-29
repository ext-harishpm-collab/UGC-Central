import json
import uuid
from pathlib import Path
from fastapi import UploadFile
from ..db.session import SessionLocal
from ..models import ImportBatch, RawImportRow, PaymentTransaction
from ..imports.pipeline import ingest_workbook

def save_upload(upload: UploadFile, root: str = "./uploads") -> str:
    Path(root).mkdir(parents=True, exist_ok=True)
    path = Path(root) / f"{uuid.uuid4().hex}_{upload.filename}"
    with open(path, "wb") as f:
        while chunk := upload.file.read(1024 * 1024):
            f.write(chunk)
    return str(path)

def import_uploaded_workbook(upload: UploadFile) -> dict:
    path = save_upload(upload)
    data = ingest_workbook(path)
    db = SessionLocal()
    try:
        existing = db.query(ImportBatch).filter(ImportBatch.checksum == data["batch_id"]).first()
        if existing:
            return {"duplicate": True, "batch_id": existing.id, "filename": existing.filename, "message": "This exact file was already imported."}

        batch = ImportBatch(
            id=data["batch_id"],
            filename=data["filename"],
            payment_period=data["inferred_period"],
            checksum=data["batch_id"],
            total_rows=data["total_rows"],
            payment_event_rows=data["payment_event_rows"],
            status="IMPORTED",
        )
        db.add(batch)

        for event in data["payment_events"]:
            raw = event["raw"]
            row_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f'{data["batch_id"]}:{event["source_sheet"]}:{event["source_row"]}'))
            db.add(RawImportRow(
                id=row_id,
                batch_id=data["batch_id"],
                source_sheet=event["source_sheet"],
                source_row=event["source_row"],
                sheet_kind=event["kind"],
                payload=json.dumps(raw, ensure_ascii=False),
            ))
            db.add(PaymentTransaction(
                id=row_id,
                author_id=event.get("author_id"),
                book_id=event.get("book_id"),
                show_id=event.get("show_id"),
                payment_type=event.get("kind"),
                amount_before_tax=event.get("amount_before_tax"),
                amount_after_tax=event.get("amount_after_tax"),
                currency="INR",
                status=event.get("status", "UNMATCHED"),
                utr=event.get("utr"),
                transaction_date=None,
                payout_id=event.get("payout_id"),
                original_status=event.get("status_raw"),
                source_file=event.get("source_file"),
                source_sheet=event.get("source_sheet"),
                source_row=event.get("source_row"),
            ))
        db.commit()
        return {
            "duplicate": False,
            "batch_id": data["batch_id"],
            "filename": data["filename"],
            "payment_period": data["inferred_period"],
            "total_rows": data["total_rows"],
            "payment_event_rows": data["payment_event_rows"],
            "sheets": data["sheets"],
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def list_imports() -> list[dict]:
    db = SessionLocal()
    try:
        return [
            {
                "batch_id": b.id,
                "filename": b.filename,
                "payment_period": b.payment_period,
                "status": b.status,
                "total_rows": b.total_rows,
                "payment_event_rows": b.payment_event_rows,
                "imported_at": b.imported_at.isoformat(),
            }
            for b in db.query(ImportBatch).order_by(ImportBatch.imported_at.desc()).all()
        ]
    finally:
        db.close()
