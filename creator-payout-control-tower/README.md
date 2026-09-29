# Creator Payout Control Tower

## One-command frontend preview from this folder

```bash
npm run dev
```

This starts Vite from the `frontend` directory. Codespaces will expose port 5173.

## Backend in a second terminal

```bash
cd backend
npm run dev:backend
```

Or:

```bash
npm run dev:backend
```

from the project root if Python dependencies are installed in the environment.

## Workflow

Monthly Cycle -> upload Incentive + Revenue Share dumps -> process -> review Author Level -> export Author CSV + QC CSV -> Payout -> Batch QC -> Freeze -> UWT -> Finance result -> Ledger.
