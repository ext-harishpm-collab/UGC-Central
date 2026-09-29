import uuid
from decimal import Decimal
from ..db.session import SessionLocal
from ..models import PayoutBatch,PayoutLine,Earning,BankAccount,PanRecord,ContractRecord,RecoveryEvent,Adjustment,ComplianceRecord,QCResult,ExceptionCase
from .qc_service import run_qc

def _one(q): return q.order_by(q.column_descriptions[0]["type"].class_.id.desc()).first() if False else None

def run_batch_qc(batch_id):
    db=SessionLocal()
    try:
        batch=db.query(PayoutBatch).filter_by(id=batch_id).first()
        if not batch:return {"status":"ERROR","reason":"Batch not found"}
        lines=db.query(PayoutLine).filter(PayoutLine.batch_id==batch_id).all()
        results=[];passed=blocked=0
        db.query(QCResult).filter(QCResult.period==batch.payment_period,QCResult.entity_type=="PAYOUT_LINE").delete(synchronize_session=False)
        for line in lines:
            flags=[]
            author=line.author_id
            bank=db.query(BankAccount).filter(BankAccount.author_id==author,BankAccount.is_current==True).first()
            pan=db.query(PanRecord).filter(PanRecord.author_id==author).order_by(PanRecord.validated_at.desc()).first()
            earns=db.query(Earning).filter(Earning.payment_period==batch.payment_period,Earning.author_id==author).all()
            rs_earn=[e for e in earns if e.reward_type=="REVENUE_SHARE" and e.exclusion_reason is None]
            contracts=[]
            for e in rs_earn:
                contracts += db.query(ContractRecord).filter(ContractRecord.book_id==e.book_id).all() if e.book_id else []
                if e.product_rs is not None:
                    matching=[c for c in contracts if c.book_id==e.book_id]
                    if not matching: flags.append({"rule_id":"CON-002","severity":"BLOCK","message":f"Missing contract RS for Book {e.book_id}"})
                    elif not any(c.contract_rs is not None and abs(float(c.contract_rs)-float(e.product_rs))<1e-9 for c in matching):
                        flags.append({"rule_id":"CON-001","severity":"BLOCK","message":f"RS mismatch for Book {e.book_id}","detected":str(e.product_rs)})
            if not bank: flags.append({"rule_id":"BANK-001","severity":"BLOCK","message":"No validated/current bank account found"})
            if not pan or pan.validated_tds_rate is None: flags.append({"rule_id":"TAX-001","severity":"BLOCK","message":"PAN/TDS source validation missing"})
            recoveries=db.query(RecoveryEvent).filter(RecoveryEvent.payment_period==batch.payment_period,RecoveryEvent.author_id==author).all()
            opening=sum((r.opening_outstanding or 0) for r in recoveries);applied=sum((r.applied or 0) for r in recoveries)
            if applied>opening+Decimal("0.01"): flags.append({"rule_id":"REC-001","severity":"BLOCK","message":"Recovery exceeds recorded outstanding","detected":str(applied),"expected":str(opening)})
            adjs=db.query(Adjustment).filter(Adjustment.payment_period==batch.payment_period,Adjustment.author_id==author).all()
            pending=[a for a in adjs if a.status!="APPROVED" or not a.reason]
            if pending: flags.append({"rule_id":"ADJ-001","severity":"BLOCK","message":"Pending or undocumented adjustment exists"})
            comps=db.query(ComplianceRecord).filter(ComplianceRecord.author_id==author).all()
            hold=[c for c in comps if c.status and c.status.upper() in {"BLOCK","HOLD","INELIGIBLE","REJECTED"}]
            if hold: flags.append({"rule_id":"CMP-001","severity":"BLOCK","message":"Compliance hold/ineligible record exists"})
            flags += run_qc({"author_id":author,"content_type":None,"incentive":float(line.gross_incentive or 0),
                              "bank_ok":bool(bank),"pan_ok":bool(pan and pan.validated_tds_rate is not None),
                              "previously_paid":False,"recovery_double":applied>opening+Decimal("0.01"),
                              "adjustment_reason":not bool(pending),"payment_threshold":100,"final_net":float(line.net_payable or 0)})["flags"]
            uniq={(f["rule_id"],f["message"]) for f in flags}
            flags=[{"rule_id":a,"severity":"BLOCK" if b.find("Missing")>=0 else next((f["severity"] for f in flags if f["rule_id"]==a and f["message"]==b),"REVIEW"),"message":b} for a,b in uniq]
            for f in flags:
                db.add(QCResult(id=uuid.uuid4().hex,period=batch.payment_period,entity_type="PAYOUT_LINE",entity_id=line.id,rule_id=f["rule_id"],severity=f["severity"],message=f["message"],detected_value=str(f.get("detected")) if f.get("detected") is not None else None,expected_value=str(f.get("expected")) if f.get("expected") is not None else None,status="OPEN"))
            line.qc_status="BLOCK" if any(f["severity"] in {"BLOCK","CRITICAL"} for f in flags) else "PASS"
            passed += line.qc_status=="PASS"; blocked += line.qc_status=="BLOCK"
            results.append({"payout_line_id":line.id,"author_id":author,"status":line.qc_status,"flags":flags})
        batch.status="QC_PASS" if blocked==0 else "QC_BLOCKED"
        db.commit()
        return {"batch_id":batch_id,"status":batch.status,"lines":len(lines),"passed":passed,"blocked":blocked,"results":results}
    except Exception:db.rollback();raise
    finally:db.close()
