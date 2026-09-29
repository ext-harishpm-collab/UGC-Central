# Phase 10 - UWT Finance result flow

The application now has a dedicated UWT importer for the fixed 13-column Finance result structure.

UWT import behavior:
1. Detect the fixed UWT header.
2. Parse bank-account JSON without converting account numbers to numeric values.
3. Normalize payment status.
4. Match first by Payout ID, then UTR, then Book ID + Amount After Tax.
5. SUCCESS closes the ledger and can create/update successful-payment bank evidence.
6. FAILED and REVERSED remain RETRYABLE.
7. UNMATCHED is not forced onto a payment and remains a reconciliation issue.
8. Retain original status/details for audit.

Operational APIs include Author 360 and Content 360 views and filtered UWT rows.

The exact Finance matching key still requires month-by-month parity validation before production use.
