from decimal import Decimal
from collections import defaultdict
from ..db.session import SessionLocal
from ..models import PaymentTransaction,PayoutBatch,PayoutLine,Earning

def close_report(period):
    db=SessionLocal()
    try:
        approved=sum((x.net_payable or 0) for x in db.query(PayoutLine).filter(PayoutLine.payment_period==period,PayoutLine.qc_status=="PASS").all())
        payments=db.query(PaymentTransaction).filter(PaymentTransaction.payment_period==period).all()
        status_amount=defaultdict(lambda:Decimal("0"))
        status_count=defaultdict(int)
        for p in payments:
            status_count[p.status]+=1;status_amount[p.status]+=p.amount_after_tax or 0
        pending=sum((x.net_payable or 0) for x in db.query(PayoutLine).filter(PayoutLine.payment_period==period,PayoutLine.freeze_status!="CLOSED").all())
        return {"period":period,
                "approved_payout_net":float(approved),
                "processed_net":float(sum(status_amount.values())),
                "success_count":status_count["SUCCESS"],"success_amount":float(status_amount["SUCCESS"]),
                "failed_count":status_count["FAILED"],"failed_amount":float(status_amount["FAILED"]),
                "reversed_count":status_count["REVERSED"],"reversed_amount":float(status_amount["REVERSED"]),
                "unmatched_count":status_count["UNMATCHED"],"unmatched_amount":float(status_amount["UNMATCHED"]),
                "pending_payout_lines":float(pending),
                "status":"CLOSED_OK" if status_count["UNMATCHED"]==0 else "CLOSE_REVIEW"}
    finally:db.close()
