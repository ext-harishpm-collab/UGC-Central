import uuid
from decimal import Decimal
from ..db.session import SessionLocal
from ..models import PayoutBatch,PayoutLine,Earning,BankAccount,PanRecord,ContractRecord,RecoveryEvent,Adjustment,ComplianceRecord,QCResult,ExceptionCase

def _add(flags,rule,severity,message,detected=None,expected=None):flags.append({"rule_id":rule,"severity":severity,"message":message,"detected":detected,"expected":expected})

def run_batch_qc(batch_id):
    db=SessionLocal()
    try:
        batch=db.query(PayoutBatch).filter_by(id=batch_id).first()
        if not batch:return {"status":"ERROR","reason":"Batch not found"}
        lines=db.query(PayoutLine).filter_by(batch_id=batch_id).all();results=[];passed=blocked=0
        db.query(QCResult).filter(QCResult.period==batch.payment_period,QCResult.entity_type=="PAYOUT_LINE").delete(synchronize_session=False)
        for line in lines:
            flags=[];aid=line.author_id
            bank=db.query(BankAccount).filter(BankAccount.author_id==aid,BankAccount.is_current==True).first()
            pan=db.query(PanRecord).filter(PanRecord.author_id==aid).order_by(PanRecord.validated_at.desc().nullslast()).first()
            if not bank:_add(flags,"BANK-001","BLOCK","No validated/current bank account")
            if not pan or pan.validated_tds_rate is None:_add(flags,"TAX-001","BLOCK","PAN/TDS source validation missing")
            earns=db.query(Earning).filter(Earning.payment_period==batch.payment_period,Earning.author_id==aid,Earning.exclusion_reason.is_(None)).all()
            for e in earns:
                if e.reward_type!="REVENUE_SHARE" or e.product_rs is None:continue
                cs=db.query(ContractRecord).filter(ContractRecord.book_id==e.book_id).all()
                if not cs:_add(flags,"CON-002","BLOCK",f"Missing contract RS for Book {e.book_id}")
                elif not any(c.contract_rs is not None and abs(float(c.contract_rs)-float(e.product_rs))<1e-9 for c in cs):
                    _add(flags,"CON-001","BLOCK",f"Contract RS mismatch for Book {e.book_id}",str(e.product_rs))
            recs=db.query(RecoveryEvent).filter(RecoveryEvent.payment_period==batch.payment_period,RecoveryEvent.author_id==aid).all()
            opening=sum((r.opening_outstanding or 0) for r in recs);applied=sum((r.applied or 0) for r in recs)
            if applied>opening+Decimal("0.01"):_add(flags,"REC-001","BLOCK","Recovery exceeds outstanding",str(applied),str(opening))
            adjs=db.query(Adjustment).filter(Adjustment.payment_period==batch.payment_period,Adjustment.author_id==aid).all()
            for a in adjs:
                if a.status!="APPROVED":_add(flags,"ADJ-001","BLOCK","Adjustment is not approved",a.status,"APPROVED")
                if not a.reason:_add(flags,"ADJ-002","BLOCK","Adjustment reason is missing")
            comps=db.query(ComplianceRecord).filter(ComplianceRecord.author_id==aid).all()
            for c in comps:
                if c.status and c.status.upper() in {"BLOCK","HOLD","INELIGIBLE","REJECTED"}:_add(flags,"CMP-001","BLOCK","Compliance hold/ineligible record",c.status)
            if line.net_payable < 100 and line.net_payable > 0:_add(flags,"PAY-001","BLOCK","Net payable is below payment threshold",str(line.net_payable),"100")
            status="BLOCK" if any(x["severity"] in {"BLOCK","CRITICAL"} for x in flags) else "PASS"
            line.qc_status=status
            for f in flags:
                db.add(QCResult(id=uuid.uuid4().hex,period=batch.payment_period,entity_type="PAYOUT_LINE",entity_id=line.id,rule_id=f["rule_id"],severity=f["severity"],message=f["message"],detected_value=f.get("detected"),expected_value=f.get("expected"),status="OPEN"))
            passed+=status=="PASS";blocked+=status=="BLOCK";results.append({"payout_line_id":line.id,"author_id":aid,"status":status,"flags":flags})
        batch.status="QC_PASS" if blocked==0 else "QC_BLOCKED";db.commit()
        return {"batch_id":batch_id,"status":batch.status,"lines":len(lines),"passed":passed,"blocked":blocked,"results":results}
    except Exception:db.rollback();raise
    finally:db.close()
