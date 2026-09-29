from decimal import Decimal
from ..db.session import SessionLocal
from ..models import Contract if False else None

def normalize_rs(v):
    try:return Decimal(str(v)).quantize(Decimal("0.0001"))
    except:return None

# Contract master adapter: source-specific parsing is intentionally kept separate from calculation.
# Until field-level validation is complete, no contract value is inferred from unrelated sheets.
def validate_rs(contract_rs, product_rs):
    c=normalize_rs(contract_rs);p=normalize_rs(product_rs)
    if c is None or p is None:return {"status":"MISSING","contract_rs":str(c) if c is not None else None,"product_rs":str(p) if p is not None else None}
    return {"status":"MATCH" if c==p else "MISMATCH","contract_rs":str(c),"product_rs":str(p)}
