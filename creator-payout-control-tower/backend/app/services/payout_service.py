from collections import defaultdict
from decimal import Decimal
from ..db.session import SessionLocal
from ..models import Earning
from .calculation_service import money,calculate,cap_amount
from .rules_service import get_rules
from .recovery_service import author_recovery,author_adjustments

def build_preview(period,marketing_cap=None,cop_cap=None,cap_mode="INDIVIDUAL",tds_rate=0):
    db=SessionLocal()
    try:
        rows=db.query(Earning).filter(Earning.payment_period==period,Earning.exclusion_reason.is_(None)).all()
        grouped=defaultdict(lambda:{"incentive":Decimal("0"),"revenue_share":Decimal("0"),"other":Decimal("0"),"earnings":[]})
        for e in rows:
            if not e.author_id:continue
            g=grouped[e.author_id]
            if e.reward_type=="INCENTIVE":g["incentive"]+=e.gross or 0
            elif e.reward_type=="REVENUE_SHARE":g["revenue_share"]+=e.gross or 0
            else:g["other"]+=e.gross or 0
            g["earnings"].append({"id":e.id,"book_id":e.book_id,"show_id":e.show_id,"type":e.reward_type,"content_type":e.content_type,"gross":float(e.gross or 0)})
        rules=get_rules(period);mrate=Decimal(str(marketing_cap if marketing_cap is not None else rules["MARKETING_CAP"]));crate=Decimal(str(cop_cap if cop_cap is not None else rules["COP_CAP"]))
        rec=author_recovery(period);adj=author_adjustments(period);out=[]
        for aid,g in grouped.items():
            gross=money(g["incentive"]+g["revenue_share"]+g["other"])
            marketing=cap_amount(gross,gross*Decimal("0.30"),mrate)
            cop=cap_amount(gross,gross*Decimal("0.30"),crate)
            adjustment=money(adj.get(aid,0));recovery=money(rec.get(aid,0))
            r=calculate({"incentive":g["incentive"],"revenue_share":g["revenue_share"],"other":g["other"],"marketing":marketing,"platform":0,"cop":cop,"flat":0,"recovery":recovery,"adjustment":adjustment,"tds_rate":tds_rate})
            out.append({"author_id":aid,**r,"earning_count":len(g["earnings"]),"lineage":g["earnings"],"marketing_cap":float(mrate),"cop_cap":float(crate),"cap_mode":cap_mode})
        return out
    finally:db.close()
