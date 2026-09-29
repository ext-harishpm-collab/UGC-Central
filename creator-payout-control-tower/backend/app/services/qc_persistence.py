import uuid
from ..db.session import SessionLocal
from ..models import QCResult,ExceptionCase

def persist_qc(period,entity_type,entity_id,flags):
    db=SessionLocal()
    try:
        created=0
        for f in flags:
            rule_id=f.get("rule_id","UNKNOWN")
            severity=f.get("severity","REVIEW")
            message=f.get("message","")
            db.add(QCResult(id=uuid.uuid4().hex,period=period,entity_type=entity_type,entity_id=entity_id,
                            rule_id=rule_id,severity=severity,message=message,
                            detected_value=str(f.get("detected")) if f.get("detected") is not None else None,
                            expected_value=str(f.get("expected")) if f.get("expected") is not None else None,
                            status="OPEN"))
            if severity in {"BLOCK","CRITICAL"}:
                db.add(ExceptionCase(id=uuid.uuid4().hex,period=period,category=rule_id,entity_type=entity_type,entity_id=entity_id,
                                     severity=severity,status="OPEN",reason=message))
            created+=1
        db.commit();return created
    except Exception:
        db.rollback();raise
    finally:db.close()
