import uuid
from datetime import datetime
from decimal import Decimal
from ..db.session import SessionLocal
from ..models import PayoutBatch,PayoutLine,PayoutLineEarning
from .payout_service import build_preview

def create_draft_batch(period,marketing_cap=None,cop_cap=None,cap_mode="INDIVIDUAL",tds_rate=0):
    preview=build_preview(period,marketing_cap,cop_cap,cap_mode,tds_rate)
    db=SessionLocal()
    try:
        batch_id=uuid.uuid4().hex
        batch=PayoutBatch(id=batch_id,payment_period=period,status="DRAFT_QC_REQUIRED",notes="Generated from payout preview; not frozen.")
        db.add(batch)
        for item in preview:
            line=PayoutLine(id=uuid.uuid4().hex,batch_id=batch_id,payment_period=period,author_id=item["author_id"],
                            gross_incentive=Decimal(str(item.get("gross_incentive",0))),gross_revenue_share=Decimal(str(item.get("gross_revenue_share",0))),
                            other_earnings=Decimal(str(item.get("other_earnings",0))),gross_payable=Decimal(str(item["gross_payable"])),
                            marketing=Decimal(str(item.get("marketing",0))),platform=Decimal(str(item.get("platform",0))),
                            cop=Decimal(str(item.get("cop",0))),flat_deduction=Decimal(str(item.get("flat",0))),
                            recovery=Decimal(str(item.get("recovery",0))),adjustment=Decimal(str(item.get("adjustment",0))),
                            tds=Decimal(str(item["tds"])),net_payable=Decimal(str(item["net_payable"])),qc_status="NOT_RUN",freeze_status="OPEN")
            db.add(line)
            for e in item.get("lineage",[]): db.add(PayoutLineEarning(id=uuid.uuid4().hex,payout_line_id=line.id,earning_id=e["id"]))
        db.commit()
        return {"batch_id":batch_id,"period":period,"status":batch.status,"line_count":len(preview),"net_payable":sum(float(x["net_payable"]) for x in preview)}
    except Exception:db.rollback();raise
    finally:db.close()

def list_batches(period=None):
    db=SessionLocal()
    try:
        q=db.query(PayoutBatch)
        if period:q=q.filter(PayoutBatch.payment_period==period)
        return [{"batch_id":b.id,"period":b.payment_period,"status":b.status,"created_at":b.created_at.isoformat(),"frozen_at":b.frozen_at.isoformat() if b.frozen_at else None} for b in q.order_by(PayoutBatch.created_at.desc()).all()]
    finally:db.close()

def freeze_batch(batch_id):
    db=SessionLocal()
    try:
        b=db.query(PayoutBatch).filter_by(id=batch_id).first()
        if not b:return {"frozen":False,"reason":"Batch not found"}
        if b.status=="FROZEN":return {"frozen":True,"batch_id":batch_id}
        blocking=db.query(PayoutLine).filter(PayoutLine.batch_id==batch_id,PayoutLine.qc_status!="PASS").count()
        if blocking:return {"frozen":False,"reason":"Blocking QC: payout lines must all have QC PASS","blocking_lines":blocking}
        b.status="FROZEN";b.frozen_at=datetime.utcnow()
        db.commit();return {"frozen":True,"batch_id":batch_id}
    finally:db.close()
