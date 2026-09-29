from collections import defaultdict
from decimal import Decimal
from ..db.session import SessionLocal
from ..models import Earning,PanRecord,ContractRecord,BankAccount
from .calculation_service import money,calculate,cap_amount
from .rules_service import get_rules
from .recovery_service import author_recovery,author_adjustments

def build_preview(period,marketing_cap=None,cop_cap=None,cap_mode="INDIVIDUAL",tds_rate=None):
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
        rules=get_rules(period)
        mrate=Decimal(str(marketing_cap if marketing_cap is not None else rules["MARKETING_CAP"]))
        crate=Decimal(str(cop_cap if cop_cap is not None else rules["COP_CAP"]))
        rec=author_recovery(period);adj=author_adjustments(period);out=[]
        for aid,g in grouped.items():
            pan=db.query(PanRecord).filter(PanRecord.author_id==aid).order_by(PanRecord.validated_at.desc().nullslast()).first()
            bank=db.query(BankAccount).filter(BankAccount.author_id==aid,BankAccount.is_current==True).first()
            tax_rate=Decimal(str(tds_rate)) if tds_rate is not None else (pan.validated_tds_rate if pan and pan.validated_tds_rate is not None else None)
            gross=money(g["incentive"]+g["revenue_share"]+g["other"])
            marketing=cap_amount(gross,gross*Decimal("0.30"),mrate)
            cop=cap_amount(gross,gross*Decimal("0.30"),crate)
            recovery=money(rec.get(aid,0));adjustment=money(adj.get(aid,0))
            r=calculate({"incentive":g["incentive"],"revenue_share":g["revenue_share"],"other":g["other"],"marketing":marketing,"platform":0,"cop":cop,"flat":0,"recovery":recovery,"adjustment":adjustment,
                         "tds_rate":tax_rate if tax_rate is not None else Decimal("0")})
            controls={"pan_source":pan.source_file if pan else None,"pan_status":pan.pan_status if pan else None,
                      "tds_rate_source":"PAN_MASTER" if pan and pan.validated_tds_rate is not None and tds_rate is None else "REQUEST_OVERRIDE" if tds_rate is not None else "MISSING",
                      "bank_verified":bool(bank),"bank_source_month":bank.source_month if bank else None,
                      "tds_ready":tax_rate is not None,"bank_ready":bool(bank)}
            out.append({"author_id":aid,**r,"earning_count":len(g["earnings"]),"lineage":g["earnings"],"marketing_cap":float(mrate),"cop_cap":float(crate),
                        "cap_mode":cap_mode,"controls":controls})
        return out
    finally:db.close()
