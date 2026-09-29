import uuid
from decimal import Decimal,ROUND_HALF_UP
from ..db.session import SessionLocal
from ..models import PaymentTransaction,PayoutLine,PayoutLineEarning,Earning,LedgerEntry

def rebuild(period):
    db=SessionLocal()
    try:
        db.query(LedgerEntry).filter(LedgerEntry.payment_period==period).delete(synchronize_session=False)
        payments=db.query(PaymentTransaction).filter(PaymentTransaction.payment_period==period).all()
        total=0
        created=0;unmatched=0
        for p in payments:
            if p.status not in {"SUCCESS","FAILED","REVERSED"}: unmatched+=1;continue
            links=[]
            if p.book_id:
                links=db.query(Earning).filter(Earning.payment_period==period,Earning.book_id==p.book_id,Earning.author_id==p.author_id,Earning.exclusion_reason.is_(None)).all()
            else:
                links=db.query(Earning).filter(Earning.payment_period==period,Earning.author_id==p.author_id,Earning.exclusion_reason.is_(None)).all()
            if not links:
                unmatched+=1;continue
            weights=[(e,Decimal(str(e.net or e.gross or 0))) for e in links]
            denom=sum((w for _,w in weights),Decimal("0"))
            if denom<=0:unmatched+=1;continue
            for i,(e,w) in enumerate(weights):
                allocation=Decimal("0")
                if p.status=="SUCCESS": allocation=(Decimal(str(p.amount_after_tax or 0))*w/denom).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
                if i==len(weights)-1 and p.status=="SUCCESS":
                    prior=sum((Decimal(str(x.finance_amount)) for x in db.query(LedgerEntry).filter(LedgerEntry.payment_transaction_id==p.id).all()),Decimal("0"))
                    allocation=Decimal(str(p.amount_after_tax or 0))-prior
                db.add(LedgerEntry(id=uuid.uuid4().hex,payment_transaction_id=p.id,payment_period=period,author_id=p.author_id,book_id=e.book_id,show_id=e.show_id,content_type=e.content_type,
                    reward_type=e.reward_type,source_earning_id=e.id,allocated_gross=e.gross or 0,allocated_net=e.net or 0,finance_amount=allocation,
                    finance_status=p.status,utr=p.utr,ledger_state="CLOSED" if p.status=="SUCCESS" else "RETRYABLE",allocation_method="PROPORTIONAL"))
                created+=1
        db.commit()
        return {"period":period,"created_entries":created,"unmatched_payments":unmatched}
    finally:db.close()

def list_entries(period=None,show_id=None,book_id=None,author_id=None,content_type=None):
    db=SessionLocal()
    try:
        q=db.query(LedgerEntry)
        if period:q=q.filter(LedgerEntry.payment_period==period)
        if show_id:q=q.filter(LedgerEntry.show_id==show_id)
        if book_id:q=q.filter(LedgerEntry.book_id==book_id)
        if author_id:q=q.filter(LedgerEntry.author_id==author_id)
        if content_type:q=q.filter(LedgerEntry.content_type==content_type)
        return [{"period":x.payment_period,"author_id":x.author_id,"book_id":x.book_id,"show_id":x.show_id,
                 "content_type":x.content_type,"reward_type":x.reward_type,"allocated_gross":float(x.allocated_gross or 0),
                 "allocated_net":float(x.allocated_net or 0),"finance_amount":float(x.finance_amount or 0),
                 "status":x.finance_status,"utr":x.utr,"ledger_state":x.ledger_state,"allocation_method":x.allocation_method} for x in q.all()]
    finally:db.close()
