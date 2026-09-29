from enum import Enum

class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REVERSED = "REVERSED"
    UNMATCHED = "UNMATCHED"

SUCCESS_VALUES = {"success", "successful", "processed", "paid", "completed"}
FAILED_VALUES = {"failed", "failure"}
REVERSED_VALUES = {"reversed", "reversal"}

def normalize_payment_status(value: str | None) -> PaymentStatus:
    v = (value or "").strip().lower()
    if v in SUCCESS_VALUES:
        return PaymentStatus.SUCCESS
    if v in FAILED_VALUES:
        return PaymentStatus.FAILED
    if v in REVERSED_VALUES:
        return PaymentStatus.REVERSED
    return PaymentStatus.UNMATCHED
