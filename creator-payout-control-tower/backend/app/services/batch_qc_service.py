from ..db.session import SessionLocal
from ..models import PayoutBatch, PayoutLine
from .qc_service import run_qc

def run_batch_qc(batch_id):
    db=SessionLocal()
    try:
        batch=db.query(PayoutBatch).filter_by(id=batch_id).first()
        if not batch:
            return {"status":"ERROR","reason":"Batch not found"}
        lines=db.query(PayoutLine).filter(PayoutLine.batch_id==batch_id).all()
        passed=0; blocked=0; results=[]
        for line in lines:
            data={"author_id":line.author_id,"content_type":None,"incentive":float(line.gross_incentive or 0),
                  "bank_ok":True,"pan_ok":True,"previously_paid":False,"recovery_double":False,
                  "adjustment_reason":True,"payment_threshold":100,"final_net":float(line.net_payable or 0)}
            r=run_qc(data)
            line.qc_status="PASS" if r["status"]=="PASS" else "BLOCK"
            passed += 1 if r["status"]=="PASS" else 0
            blocked += 1 if r["status"]!="PASS" else 0
            results.append({"payout_line_id":line.id,"author_id":line.author_id,**r})
        batch.status="QC_PASS" if blocked==0 else "QC_BLOCKED"
        db.commit()
        return {"batch_id":batch_id,"status":batch.status,"lines":len(lines),"passed":passed,"blocked":blocked,"results":results[:2000]}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
