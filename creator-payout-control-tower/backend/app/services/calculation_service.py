from decimal import Decimal, ROUND_HALF_UP
D=Decimal

def money(v): return D(str(v or 0)).quantize(D("0.0001"),rounding=ROUND_HALF_UP)
def cap_amount(requested, base, cap_rate): return min(money(requested), max(D("0"), money(base)*money(cap_rate)))
def calculate(i):
    gross=money(i.get("incentive"))+money(i.get("revenue_share"))+money(i.get("other"))
    deductions=money(i.get("marketing"))+money(i.get("platform"))+money(i.get("cop"))+money(i.get("flat"))+money(i.get("recovery"))
    pre=money(gross-deductions+money(i.get("adjustment")))
    tds=money(pre*money(i.get("tds_rate")))
    return {"gross_payable":str(gross),"pre_tds":str(pre),"tds":str(tds),"net_payable":str(money(pre-tds)),
            "marketing":str(money(i.get("marketing"))),"platform":str(money(i.get("platform"))),"cop":str(money(i.get("cop"))),
            "recovery":str(money(i.get("recovery"))),"adjustment":str(money(i.get("adjustment")))}
