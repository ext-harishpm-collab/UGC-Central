from collections import defaultdict
from decimal import Decimal
from ..db.session import SessionLocal
from ..models import PaymentTransaction

def month_breakdown(month=None):
    db=SessionLocal()
    try:
        q=db.query(PaymentTransaction)
        if month:q=q.filter(PaymentTransaction.payment_period==month)
        rows=q.all()
        by_type=defaultdict(lambda:{"count":0,"before_tax":Decimal("0"),"after_tax":Decimal("0"),"SUCCESS":0,"FAILED":0,"REVERSED":0,"UNMATCHED":0})
        by_status=defaultdict(lambda:{"count":0,"after_tax":Decimal("0")})
        for r in rows:
            t=r.content_type or "UNKNOWN";b=by_type[t];b["count"]+=1
            b["before_tax"]+=r.amount_before_tax or 0;b["after_tax"]+=r.amount_after_tax or 0
            if r.status in b:b[r.status]+=1
            s=by_status[r.status];s["count"]+=1;s["after_tax"]+=r.amount_after_tax or 0
        def clean(x):
            return {k:(float(v) if isinstance(v,Decimal) else v) for k,v in x.items()}
        return {"month":month,"content":{k:clean(v) for k,v in by_type.items()},"status":{k:clean(v) for k,v in by_status.items()}}
    finally:db.close()
