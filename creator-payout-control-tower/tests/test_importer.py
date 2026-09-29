from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.imports.inspector import sheet_kind
from app.imports.pipeline import infer_period
def test_sheet_kinds():
    assert sheet_kind("uwt final")=="uwt"
    assert sheet_kind("Fin_Success_Novel")=="finance_success"
    assert sheet_kind("Fin_Reversal")=="finance_reversal"
    assert sheet_kind("Payment Status Dump")=="payment_status"
def test_infer_period():
    assert infer_period("Aug'26 Payments.xlsx")=="Aug 2026"
    assert infer_period("Jul'26 Payments.xlsx")=="Jul 2026"
