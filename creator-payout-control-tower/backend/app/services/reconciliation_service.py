from ..db.session import SessionLocal
from ..models import PaymentTransaction, ReconciliationEvent

SUCCESS={"success","successful","processed","paid","completed"}
FAILED={"failed","failure"}
REVERSED={"reversed","reversal"}
def normalize(v):
    x=(v or "").strip().lower()
    if x in SUCCESS:return "SUCCESS"
    if x in FAILED:return "FAILED"
    if x in REVERSED:return "REVERSED"
    return "UNMATCHED"

def reconcile(payout_id=None,utr=None,author_id=None,book_id=None,amount=None,raw_status=None):
    db=SessionLocal()
    try:
        row=None; match="NONE"
        if payout_id:
            row=db.query(PaymentTransaction).filter(PaymentTransaction.payout_id==payout_id).first(); match="PAYOUT_ID" if row else match
        if not row and utr:
            row=db.query(PaymentTransaction).filter(PaymentTransaction.utr==utr).first(); match="UTR" if row else match
        if not row and author_id and book_id and amount is not None:
            row=db.query(PaymentTransaction).filter(PaymentTransaction.author_id==author_id,PaymentTransaction.book_id==book_id,PaymentTransaction.amount_after_tax==amount).first(); match="AUTHOR_BOOK_AMOUNT" if row else match
        status=normalize(raw_status)
        if not row:return {"matched":False,"status":status,"reason":"No deterministic match found"}
        row.status=status
        row.ledger_state="CLOSED" if status=="SUCCESS" else "RETRYABLE" if status in {"FAILED","REVERSED"} else "OPEN"
        db.add(ReconciliationEvent(payment_transaction_id=row.id,match_type=match,finance_status=status,ledger_state=row.ledger_state))
        db.commit()
        return {"matched":True,"payment_transaction_id":row.id,"status":status,"ledger_state":row.ledger_state,"match_type":match}
    finally:db.close()
