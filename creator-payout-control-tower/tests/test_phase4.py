from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
from app.services.calculation_service import calculate
from app.services.qc_service import run_qc
from app.services.reconciliation_service import normalize

def test_calculation():
    r=calculate({"incentive":100,"revenue_share":900,"marketing":100,"tds_rate":0.1})
    assert r["gross_payable"]=="1000.0000"
    assert r["net_payable"]=="810.0000"

def test_qc_blocks_n2a_incentive():
    r=run_qc({"author_id":"A1","content_type":"N2A/A2A","incentive":10,"bank_ok":True,"pan_ok":True,"adjustment_reason":True,"final_net":200})
    assert r["status"]=="BLOCK"
    assert any(f["rule_id"]=="ELG-002" for f in r["flags"])

def test_status_normalization():
    assert normalize("processed")=="SUCCESS"
    assert normalize("failed")=="FAILED"
    assert normalize("reversal")=="REVERSED"
