from ..db.session import SessionLocal
from ..models import PaymentTransaction

def list_ledger(month=None,content_type=None,status=None,show_id=None,book_id=None,author_id=None):
    db=SessionLocal()
    try:
        q=db.query(PaymentTransaction)
        if month:q=q.filter(PaymentTransaction.payment_period==month)
        if content_type:q=q.filter(PaymentTransaction.content_type==content_type)
        if status:q=q.filter(PaymentTransaction.status==status)
        if show_id:q=q.filter(PaymentTransaction.show_id==show_id)
        if book_id:q=q.filter(PaymentTransaction.book_id==book_id)
        if author_id:q=q.filter(PaymentTransaction.author_id==author_id)
        out=[]
        for r in q.order_by(PaymentTransaction.source_row.asc()).limit(10000).all():
            out.append({
                "payment_id":r.id,"payment_period":r.payment_period,"author_id":r.author_id,"book_id":r.book_id,"show_id":r.show_id,
                "content_type":r.content_type or "UNKNOWN","payment_type":r.payment_type,
                "amount_before_tax":float(r.amount_before_tax) if r.amount_before_tax is not None else None,
                "amount_after_tax":float(r.amount_after_tax) if r.amount_after_tax is not None else None,
                "status":r.status,"utr":r.utr,"payout_id":r.payout_id,"ledger_state":r.ledger_state,
                "source_file":r.source_file,"source_sheet":r.source_sheet,"source_row":r.source_row
            })
        return out
    finally:db.close()

def ledger_summary(month=None):
    rows=list_ledger(month=month)
    by_status={};by_type={}
    for r in rows:
        by_status[r["status"]]=by_status.get(r["status"],0)+1
        by_type[r["content_type"]]=by_type.get(r["content_type"],0)+1
    return {"total":len(rows),"by_status":by_status,"by_content_type":by_type}
