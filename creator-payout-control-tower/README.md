# Creator Payout Control Tower

Local-first internal payout operations platform.

## Run in Codespaces

Frontend:
```bash
cd /workspaces/UGC-Central/creator-payout-control-tower/frontend
npm install
npm run dev -- --host 0.0.0.0
```

Backend:
```bash
cd /workspaces/UGC-Central/creator-payout-control-tower/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Lovable remains deferred until historical parity, calculations, QC, UWT reconciliation and ledger validation are complete.
