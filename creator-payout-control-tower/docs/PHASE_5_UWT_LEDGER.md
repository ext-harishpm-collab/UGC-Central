# Phase 5 - UWT and ledger processing

The fixed UWT interface is:
Payout Type, Book ID, User Bank Account, Amount Before Tax, Currency, Amount After Tax, Payout Status, UTR, TDS%, Transaction Date, Payout Id, Mode, Status Details.

Finance results normalize to SUCCESS, FAILED, REVERSED or UNMATCHED. Reconciliation uses deterministic keys in this order: Payout ID, UTR, then Book ID + processed amount. A matched SUCCESS closes the transaction. FAILED/REVERSED remain retryable. Unmatched results are not forced onto a payout.

Ledger APIs support filtering by month, content type, status, Show ID, Book ID and Author ID. Monthly breakdown separates content categories and status totals.

This is a foundation; exact field-level Finance matching rules still require validation against all historical UWT files before production use.
