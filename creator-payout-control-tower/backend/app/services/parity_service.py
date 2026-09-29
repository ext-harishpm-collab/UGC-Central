from collections import defaultdict
from decimal import Decimal
from ..db.session import SessionLocal
from ..models import Earning, PaymentTransaction

def classify(content,reward):
    x=(content or "").upper()
    if "N2A" in x or "A2A" in x: return "N2A/A2A"
    if "SERIES" in x: return "SERIES"
    if "NOVEL" in x: return "NOVEL"
    if "INCENTIVE" in (reward or "").upper(): return "INCENTIVE"
    return x or "UNKNOWN"

def parity(period):
    db=SessionLocal()
    try:
        eg=defaultdict(lambda: [0,Decimal("0")])
        pn=defaultdict(lambda: [0,Decimal("0")])
        for r in db.query(Earning).filter(Earning.payment_period==period).all():
            key=(r.author_id or "MISSING",r.book_id or "MISSING",r.show_id or "MISSING",classify(r.content_type,r.reward_type))
            eg[key][0]+=1
            if r.exclusion_reason is None: eg[key][1]+=r.gross or 0
        for r in db.query(PaymentTransaction).filter(PaymentTransaction.payment_period==period).all():
            key=(r.author_id or "MISSING",r.book_id or "MISSING",r.show_id or "MISSING",classify(r.content_type,r.payment_type))
            pn[key][0]+=1;pn[key][1]+=r.amount_after_tax or 0
        details=[]
        for key in sorted(set(eg)|set(pn)):
            a=eg[key];p=pn[key];delta=a[1]-p[1]
            details.append({"author_id":key[0],"book_id":key[1],"show_id":key[2],"content_type":key[3],
                            "earning_rows":a[0],"payment_rows":p[0],"earning_gross":float(a[1]),"payment_net":float(p[1]),
                            "delta":float(delta),"status":"MATCH" if abs(delta)<Decimal("0.01") else "REVIEW"})
        return {"period":period,"summary":{"groups":len(details),"match":sum(x["status"]=="MATCH" for x in details),
                "review":sum(x["status"]=="REVIEW" for x in details),
                "earning_gross":sum(x["earning_gross"] for x in details),
                "payment_net":sum(x["payment_net"] for x in details),
                "delta":sum(x["delta"] for x in details)},"details":details}
    finally:
        db.close()
