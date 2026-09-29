from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
from app.calculation import calculate_payout as legacy_calc if False else None
