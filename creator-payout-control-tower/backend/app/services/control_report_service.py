from collections import defaultdict
from decimal import Decimal
from ..db.session import SessionLocal
from ..models import Earning,QCResult,PayoutBatch,PayoutLine,PaymentTransaction,LedgerEntry

def control_report(period):
    db=SessionLocal()
    try:
        earnings=db.query(Earning).filter(Earning.payment_period==period).all()
        qc=db.query(QCResult).filter(QCResult.period==period).all()
        batches=db.query(PayoutBatch).filter(PayoutBatch.payment_period==period).all()
        lines=db.query(PayoutLine).filter(PayoutLine.payment_period==period).all()
        payments=db.query(PaymentTransaction).filter(PaymentTransaction.payment_period==period).all()
        ledger=db.query(LedgerEntry).filter(LedgerEntry.payment_period==period).all()
        eligible=[e for e in earnings if e.exclusion_reason is None]
        types=defaultdict(lambda:{"rows":0,"eligible":0,"gross":Decimal("0")})
        for e in earnings:
            k=e.content_type or "UNKNOWN"
            types[k]["rows"]+=1
            if e.exclusion_reason is None:
                types[k]["eligible"]+=1
                types[k]["gross"]+=e.gross or 0
        open_block=sum(1 for x in qc if x.status=="OPEN" and x.severity in {"BLOCK","CRITICAL"})
        open_review=sum(1 for x in qc if x.status=="OPEN" and x.severity=="REVIEW")
        line_pass=sum(1 for x in lines if x.qc_status=="PASS")
        line_block=sum(1 for x in lines if x.qc_status=="BLOCK")
        success=[p for p in payments if p.status=="SUCCESS"]
        failed=[p for p in payments if p.status=="FAILED"]
        reversed_rows=[p for p in payments if p.status=="REVERSED"]
        unmatched=[p for p in payments if p.status=="UNMATCHED"]
        return {
            "period":period,
            "source":{"rows":len(earnings),"eligible_rows":len(eligible),
                      "eligible_gross":float(sum((e.gross or 0) for e in eligible)),
                      "excluded_rows":len(earnings)-len(eligible),
                      "content":{k:{"rows":v["rows"],"eligible":v["eligible"],"gross":float(v["gross"])} for k,v in types.items()}},
            "qc":{"open_block":open_block,"open_review":open_review,
                  "status":"BLOCKED" if open_block else "REVIEW" if open_review else "PASS"},
            "payout":{"batches":len(batches),"lines":len(lines),"qc_pass":line_pass,"qc_block":line_block,
                      "approved_net":float(sum((x.net_payable or 0) for x in lines if x.qc_status=="PASS"))},
            "finance":{"success_rows":len(success),"success_net":float(sum((p.amount_after_tax or 0) for p in success)),
                       "failed_rows":len(failed),"reversed_rows":len(reversed_rows),"unmatched_rows":len(unmatched)},
            "ledger":{"entries":len(ledger),"success_entries":sum(1 for x in ledger if x.finance_status=="SUCCESS"),
                      "retryable_entries":sum(1 for x in ledger if x.ledger_state=="RETRYABLE"),
                      "allocated_finance":float(sum((x.finance_amount or 0) for x in ledger))},
            "overall_status":"BLOCKED" if open_block or line_block or unmatched else
                            "REVIEW" if open_review or failed or reversed_rows else "PASS"
        }
    finally:
        db.close()
