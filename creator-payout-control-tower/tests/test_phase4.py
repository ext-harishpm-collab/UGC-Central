from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.calculation_service import calculate
from app.services.qc_service import run_qc

def test_calculation():
    r = calculate({"incentive":100,"revenue_share":900,"marketing":100,"platform":0,"cop":0,"flat":0,"recovery":0,"adjustment":0,"tds_rate":0.10})
    assert r["gross_payable"] == "1000.0000"
    assert r["net_payable"] == "810.0000"

def test_n2a_incentive_blocks():
    r = run_qc({"author_id":"A1","content_type":"N2A/A2A","incentive":10,"contract_rs":7,"product_rs":7,"bank_ok":True,"pan_ok":True,"final_net":200})
    assert r["status"] == "BLOCK"
    assert any(x["rule_id"] == "ELG-002" for x in r["flags"])
