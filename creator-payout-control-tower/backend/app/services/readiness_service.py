from collections import Counter
from ..db.session import SessionLocal
from ..models import Earning, PaymentTransaction, PayoutBatch

def cycle_readiness(period):
    db=SessionLocal()
    try:
        earnings=db.query(Earning).filter(Earning.payment_period==period).all()
        payments=db.query(PaymentTransaction).filter(PaymentTransaction.payment_period==period).all()
        batches=db.query(PayoutBatch).filter(PayoutBatch.payment_period==period).all()
        checks=[]
        missing_ids=sum(1 for e in earnings if not e.author_id or not e.book_id)
        excluded=sum(1 for e in earnings if e.exclusion_reason)
        unmatched=sum(1 for p in payments if p.status=="UNMATCHED")
        duplicate_utrs=sum(1 for n in Counter(p.utr for p in payments if p.utr).values() if n>1)
        checks.append({"code":"ID-001","label":"Earnings missing Author/Book","count":missing_ids,"blocking":True})
        checks.append({"code":"ELG-001","label":"Excluded earnings retained for audit","count":excluded,"blocking":False})
        checks.append({"code":"PAY-001","label":"Unmatched payment results","count":unmatched,"blocking":True})
        checks.append({"code":"DUP-001","label":"Duplicate UTR values","count":duplicate_utrs,"blocking":True})
        checks.append({"code":"BATCH-001","label":"Existing payout batches","count":len(batches),"blocking":False})
        ready=not any(c["blocking"] and c["count"] for c in checks)
        return {"period":period,"ready":ready,"checks":checks}
    finally:
        db.close()
