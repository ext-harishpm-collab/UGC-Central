from sqlalchemy import func
from ..db.session import SessionLocal
from ..models import Earning,PaymentTransaction

def parity(period):
    db=SessionLocal()
    try:
        eg=sum(float(x.gross or 0) for x in db.query(Earning).filter(Earning.payment_period==period,Earning.exclusion_reason.is_(None)).all())
        pn=sum(float(x.amount_after_tax or 0) for x in db.query(PaymentTransaction).filter(PaymentTransaction.payment_period==period).all())
        return {"period":period,"earning_gross_total":eg,"finance_net_total":pn,"delta":eg-pn,"status":"MATCH" if abs(eg-pn)<0.01 else "REVIEW"}
    finally:db.close()
