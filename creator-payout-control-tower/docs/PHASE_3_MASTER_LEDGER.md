# Phase 3 - Historical Master and Ledger Foundation

The local application now has APIs for:
- historical workbook import
- persistent author/content/payment records
- master summary
- ledger summary and filtered ledger rows
- effective-dated configurable payout rules

Important controls:
- historical records are append-oriented
- UWT is treated as a fixed external interface
- payment statuses normalize to SUCCESS / FAILED / REVERSED / UNMATCHED
- only SUCCESS is eligible as a source for future bank-account verification evidence
- content can be filtered by NOVEL / SERIES / N2A/A2A when classification data is populated

The full payout calculation and Show-level Finance reconciliation engine is intentionally the next milestone; no direct money movement is implemented.
