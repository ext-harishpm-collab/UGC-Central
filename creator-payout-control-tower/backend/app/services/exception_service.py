from sqlalchemy import func
from ..db.session import SessionLocal
from ..models import QCResult,ExceptionCase
import uuid

def open_exceptions(period=None):
    db=SessionLocal()
    try:
        q=db.query(QCResult).filter(QCResult.status=="OPEN")
        if period:q=q.filter(QCResult.period==period)
        out=[]
        for r in q.all():
            out.append({"rule_id":r.rule_id,"severity":r.severity,"entity_type":r.entity_type,"entity_id":r.entity_id,"message":r.message,"status":r.status})
        return out
    finally:db.close()
