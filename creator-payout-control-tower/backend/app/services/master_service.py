import uuid
from sqlalchemy import func
from ..db.session import SessionLocal
from ..models import Author,BankAccount,ContentItem,PaymentTransaction
from .status import PaymentStatus
def nid(p):return f"{p}_{uuid.uuid4().hex}"
def enrich_from_payment_events():
    db=SessionLocal()
    try:
        rows=db.query(PaymentTransaction).all();ac=cc=bc=0
        for r in rows:
            if r.author_id:
                a=db.query(Author).filter_by(author_id=r.author_id).first()
                if not a:db.add(Author(id=nid("author"),author_id=r.author_id,first_seen=r.transaction_date,last_seen=r.transaction_date));ac+=1
            if r.book_id or r.show_id:
                q=db.query(ContentItem)
                if r.book_id:q=q.filter(ContentItem.book_id==r.book_id)
                elif r.show_id:q=q.filter(ContentItem.show_id==r.show_id)
                if not q.first():db.add(ContentItem(id=nid("content"),book_id=r.book_id,show_id=r.show_id,author_id=r.author_id));cc+=1
            if r.status==PaymentStatus.SUCCESS.value and r.author_id and r.account_number:
                q=db.query(BankAccount).filter_by(author_id=r.author_id,account_number=str(r.account_number),ifsc=r.ifsc)
                b=q.first()
                if not b:
                    b=BankAccount(id=nid("bank"),author_id=r.author_id,account_number=str(r.account_number),ifsc=r.ifsc,bank_name=r.bank_name,
                                  verification_status="SUCCESS_PAYMENT_EVIDENCE",successful_payment_count=1,
                                  first_successful_payment=r.transaction_date,last_successful_payment=r.transaction_date,
                                  source_month=r.payment_period,is_current=True)
                    db.add(b);bc+=1
                else:
                    b.successful_payment_count+=1
                    b.last_successful_payment=r.transaction_date or b.last_successful_payment
                    b.is_current=True
        db.commit();return {"authors_created":ac,"content_created":cc,"bank_records_created_or_updated":bc}
    finally:db.close()
def master_summary():
    db=SessionLocal()
    try:return {"authors":db.query(func.count(Author.id)).scalar() or 0,"bank_accounts":db.query(func.count(BankAccount.id)).scalar() or 0,
                "content_items":db.query(func.count(ContentItem.id)).scalar() or 0,"payment_transactions":db.query(func.count(PaymentTransaction.id)).scalar() or 0}
    finally:db.close()
