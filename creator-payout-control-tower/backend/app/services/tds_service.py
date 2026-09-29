from decimal import Decimal

def normalize_pan_status(v):
    x=(str(v).strip().lower() if v is not None else "")
    if x in {"valid","operative"}:return "VALID"
    if x in {"invalid","inoperative"}:return "INVALID"
    if x in {"","none","nan"}:return "MISSING"
    return "REVIEW"

def effective_tds_rate(pan_status, standard_rate=0.10, invalid_rate=0.20):
    s=normalize_pan_status(pan_status)
    if s=="VALID":return Decimal(str(standard_rate))
    if s=="INVALID":return Decimal(str(invalid_rate))
    return None
