from decimal import Decimal

def normalize_rs(value):
    try:
        return Decimal(str(value)).quantize(Decimal("0.0001"))
    except Exception:
        return None

def validate_rs(contract_rs, product_rs):
    contract = normalize_rs(contract_rs)
    product = normalize_rs(product_rs)
    if contract is None or product is None:
        return {"status":"MISSING","contract_rs":str(contract) if contract is not None else None,
                "product_rs":str(product) if product is not None else None}
    return {"status":"MATCH" if contract == product else "MISMATCH",
            "contract_rs":str(contract),"product_rs":str(product)}
