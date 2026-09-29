from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.calculation_service import calculate
from app.services.qc_service import run_qc
from app.services.reconciliation_service import reconcile

def test_calculation():
    result = calculate({"incentive":100,"revenue_share":900,"marketing":100,"platform":0,"cop":0,"flat":0,"recovery":0,"adjustment":0,"tds_rate":0.10})
    assert result["gross_payable"] == "1000.0000"
    assert result["net_payable"] == "810.0000"

def test_n2a_incentive_is_blocked():
    result = run_qc({"author_id":"A1","content_type":"N2A/A2A","incentive":10,"contract_rs":7,"product_rs":7,"bank_ok":True,"pan_ok":True,"previously_paid":False,"recovery_double":False,"adjustment_reason":True,"payment_threshold":100,"final_net":200})
    assert result["status"] == "BLOCK"
    assert any(flag["rule_id"] == "ELG-002" for flag in result["flags"])

def test_reconciliation_endpoint_logic_exists():
    assert callable(reconcile)
