from datetime import datetime
from decimal import Decimal
import uuid
from ..db.session import SessionLocal
from ..models import RuleConfig

DEFAULTS={"MARKETING_CAP":Decimal("0.30"),"COP_CAP":Decimal("0.30"),"PLATFORM_RATE":Decimal("0"),"FLAT_DEDUCTION_RATE":Decimal("0"),"PAYMENT_THRESHOLD":Decimal("100")}

def get_rules(period=None):
    db=SessionLocal()
    try:
        result={k:float(v) for k,v in DEFAULTS.items()}
        for key in DEFAULTS:
            q=db.query(RuleConfig).filter(RuleConfig.rule_key==key,RuleConfig.is_active==True)
            if period:
                try:
                    dt=datetime.strptime(period,"%b %Y")
                    q=q.filter((RuleConfig.effective_from==None)|(RuleConfig.effective_from<=dt))
                    q=q.filter((RuleConfig.effective_to==None)|(RuleConfig.effective_to>=dt))
                except ValueError:pass
            row=q.order_by(RuleConfig.effective_from.desc().nullslast()).first()
            if row and row.value_numeric is not None:result[key]=float(row.value_numeric)
        return result
    finally:db.close()

def save_rule(rule_key,value,effective_from=None,effective_to=None,reason=None,approved_by=None):
    if rule_key not in DEFAULTS:raise ValueError("Unsupported rule key")
    db=SessionLocal()
    try:
        row=RuleConfig(id=uuid.uuid4().hex,rule_key=rule_key,scope_type="GLOBAL",value_numeric=Decimal(str(value)),
                       effective_from=datetime.fromisoformat(effective_from) if effective_from else None,
                       effective_to=datetime.fromisoformat(effective_to) if effective_to else None,
                       reason=reason,approved_by=approved_by,is_active=True)
        db.add(row);db.commit()
        return {"id":row.id,"rule_key":row.rule_key,"value":float(row.value_numeric)}
    finally:db.close()
