from fastapi import APIRouter
from ..services.status import normalize_payment_status

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "service": "creator-payout-control-tower", "phase": 1}

@router.get("/status/normalize/{raw_status}")
def normalize(raw_status: str):
    return {"input": raw_status, "normalized": normalize_payment_status(raw_status).value}

@router.get("/config/rule-keys")
def rule_keys():
    return {
        "configurable": [
            "MARKETING_CAP",
            "COP_CAP",
            "PLATFORM_RATE",
            "FLAT_DEDUCTION_RATE",
            "PAYMENT_THRESHOLD"
        ],
        "note": "Values are effective-dated and approval-controlled."
    }
