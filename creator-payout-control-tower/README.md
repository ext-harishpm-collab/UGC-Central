# Creator Payout Control Tower

Local-first internal payout operations platform.

## Current development
- Phase 1: database/application foundation
- Phase 2: historical workbook import
- Phase 3: historical master and ledger foundation
- Phase 4: calculation + mandatory QC
- Phase 5: UWT reconciliation
- Phase 6: historical backfill and content lineage
- Phase 7: Incentive/Revenue Share earnings ingestion
- Phase 8: author payout preview with configurable caps

## Local Codespaces
Frontend:
npm install
npm run dev -- --host 0.0.0.0

Backend:
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Lovable is intentionally deferred until historical parity, calculation, QC and UWT/ledger validation are complete.
