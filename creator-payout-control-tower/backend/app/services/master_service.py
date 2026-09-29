import uuid
from sqlalchemy import func
from ..db.session import SessionLocal
from ..models import Author, BankAccount, ContentItem, PaymentTransaction
from .status import PaymentStatus

def new_id(prefix:str)->str:return f"{prefix}_{uuid.uuid4().hex}"

def enrich_from_payment_events()->dict:
    db=SessionLocal()
    try:
        rows=db.query(PaymentTransaction).all()
        authors_created=content_created=bank_created=0
        for r in rows:
            if r.author_id:
                a=db.query(Author).filter_by(author_id=r.author_id).first()
                if not a:
                    a=Author(id=new_id("author"),author_id=r.author_id,first_seen=r.transaction_date,last_seen=r.transaction_date)
                    db.add(a); authors_created+=1
                elif r.transaction_date and (not a.last_seen or r.transaction_date>a.last_seen):
                    a.last_seen=r.transaction_date
            if r.book_id or r.show_id:
                q=db.query(ContentItem)
                if r.book_id:q=q.filter(ContentItem.book_id==r.book_id)
                elif r.show_id:q=q.filter(ContentItem.show_id==r.show_id)
                if not q.first():
                    db.add(ContentItem(id=new_id("content"),book_id=r.book_id,show_id=r.show_id,author_id=r.author_id))
                    content_created+=1
        # Bank enrichment intentionally considers SUCCESS only.
        for r in rows:
            if r.status!=PaymentStatus.SUCCESS.value or not r.author_id:continue
            # Phase 3 reads bank evidence from raw UWT payload only when importer exposes the fields.
            payload_hint=None
            raw_row=db.query(PaymentTransaction).filter_by(id=r.id).first()
            if not raw_row:continue
        db.commit()
        return {"authors_created":authors_created,"content_created":content_created,"bank_records_created_or_updated":bank_created}
    finally:db.close()

def master_summary()->dict:
    db=SessionLocal()
    try:
        return {
            "authors":db.query(func.count(Author.id)).scalar() or 0,
            "bank_accounts":db.query(func.count(BankAccount.id)).scalar() or 0,
            "content_items":db.query(func.count(ContentItem.id)).scalar() or 0,
            "payment_transactions":db.query(func.count(PaymentTransaction.id)).scalar() or 0,
        }
    finally:db.close()
