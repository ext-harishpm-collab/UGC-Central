from collections import defaultdict
from decimal import Decimal
import json
from ..db.session import SessionLocal
from ..models import Earning,PanRecord,ContractRecord,BankAccount,RawImportRow,MonthlyRun,RuleConfig
from .calculation_service import money,calculate,cap_amount
from .rules_service import get_rules
from .recovery_service import author_recovery,author_adjustments


def _monthly_mapping(db, period):
    prefix = "monthly_mapping::{}::".format(period)
    rows = db.query(RuleConfig).filter(RuleConfig.scope_type == "MONTHLY_COLUMN_MAPPING").all()
    return {row.rule_key[len(prefix):]: row.value_text or "" for row in rows if row.rule_key.startswith(prefix)}


def _raw_value_for_earning(db, earning, column_name):
    if not column_name:
        return None
    runs = db.query(MonthlyRun).filter(MonthlyRun.period == earning.payment_period).all()
    run_ids = [run.id for run in runs]
    if not run_ids:
        return None
    raw = db.query(RawImportRow).filter(
        RawImportRow.batch_id.in_(run_ids),
        RawImportRow.source_sheet == earning.source_sheet,
        RawImportRow.source_row == earning.source_row,
    ).first()
    if not raw:
        return None
    try:
        payload = json.loads(raw.payload or "{}")
        return payload.get(column_name)
    except Exception:
        return None


def _decimal_source_value(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).replace(",", "").replace("₹", "").strip())
    except Exception:
        return None


def _tds_factor(value):
    number = _decimal_source_value(value)
    if number is None:
        return None
    if number > Decimal("1"):
        number = number / Decimal("100")
    return max(Decimal("0"), min(Decimal("1"), number))

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
        mapping=_monthly_mapping(db,period)
        inc_gross_col=mapping.get("INCENTIVE_DUMP::gross","")
        rs_gross_col=mapping.get("REVENUE_SHARE_DUMP::gross","")
        tds_factor_col=mapping.get("ALL::tds_factor","")
        if inc_gross_col or rs_gross_col:
            remapped=defaultdict(lambda:{"incentive":Decimal("0"),"revenue_share":Decimal("0"),"other":Decimal("0"),"earnings":[]})
            for earning in rows:
                if not earning.author_id:
                    continue
                group=remapped[earning.author_id]
                gross_col=inc_gross_col if earning.reward_type=="INCENTIVE" else rs_gross_col
                mapped=_decimal_source_value(_raw_value_for_earning(db,earning,gross_col)) if gross_col else None
                amount=mapped if mapped is not None else (earning.gross or Decimal("0"))
                if earning.reward_type=="INCENTIVE":
                    group["incentive"] += amount
                elif earning.reward_type=="REVENUE_SHARE":
                    group["revenue_share"] += amount
                else:
                    group["other"] += amount
                group["earnings"].append({"id":earning.id,"book_id":earning.book_id,"show_id":earning.show_id,"type":earning.reward_type,"content_type":earning.content_type,"gross":float(amount)})
            grouped=remapped
        for aid,g in grouped.items():
            pan=db.query(PanRecord).filter(PanRecord.author_id==aid).order_by(PanRecord.validated_at.desc().nullslast()).first()
            bank=db.query(BankAccount).filter(BankAccount.author_id==aid,BankAccount.is_current==True).first()
            mapped_tds=[]
            if tds_factor_col and tds_rate is None:
                for earning in rows:
                    if earning.author_id != aid:
                        continue
                    factor=_tds_factor(_raw_value_for_earning(db,earning,tds_factor_col))
                    if factor is not None:
                        amount=Decimal(str(next((x["gross"] for x in g["earnings"] if x["id"]==earning.id), 0)))
                        mapped_tds.append((amount,factor))
            if mapped_tds and sum(x[0] for x in mapped_tds) > 0:
                total_weight=sum(x[0] for x in mapped_tds)
                tax_rate=sum(amount*factor for amount,factor in mapped_tds)/total_weight
                tds_source="DUMP_COLUMN_WEIGHTED"
            else:
                tax_rate=Decimal(str(tds_rate)) if tds_rate is not None else (pan.validated_tds_rate if pan and pan.validated_tds_rate is not None else None)
                tds_source="REQUEST_OVERRIDE" if tds_rate is not None else "PAN_MASTER" if pan and pan.validated_tds_rate is not None else "MISSING"
            gross=money(g["incentive"]+g["revenue_share"]+g["other"])
            marketing=cap_amount(gross,gross*Decimal("0.30"),mrate)
            cop=cap_amount(gross,gross*Decimal("0.30"),crate)
            recovery=money(rec.get(aid,0));adjustment=money(adj.get(aid,0))
            r=calculate({"incentive":g["incentive"],"revenue_share":g["revenue_share"],"other":g["other"],"marketing":marketing,"platform":0,"cop":cop,"flat":0,"recovery":recovery,"adjustment":adjustment,
                         "tds_rate":tax_rate if tax_rate is not None else Decimal("0")})
            controls={"pan_source":pan.source_file if pan else None,"pan_status":pan.pan_status if pan else None,
                      "tds_rate_source":tds_source,
                      "bank_verified":bool(bank),"bank_source_month":bank.source_month if bank else None,
                      "tds_ready":tax_rate is not None,"bank_ready":bool(bank)}
            out.append({"author_id":aid,**r,"earning_count":len(g["earnings"]),"lineage":g["earnings"],"marketing_cap":float(mrate),"cop_cap":float(crate),
                        "cap_mode":cap_mode,"controls":controls})
        return out
    finally:db.close()
