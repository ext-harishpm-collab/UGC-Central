# Phase 6 - Historical backfill and content lineage

The backfill endpoint accepts processed XLSX/XLSM workbooks and builds reusable historical authors, Book->Show mappings, Novel/Series content classification and payment-result history.

Known source patterns from the provided workbooks:
- Show Book Mapping: Book ID -> Show ID -> Author UID.
- RS Final / Inc Final: IP Type and Book ID for Novel/Series classification.
- UTR Details: Finance result rows with account, IFSC, amount, status and UTR.
- Payment Status Dump: reward type, payout month, Book ID, payout status, processed net, UTR and payment date.
- Author Level Novel / Series / N2A-A2A: Author-level monthly totals and reference bank details.

Bank records from Author Level sheets are reference information only. A bank account becomes successful-payment evidence only from a SUCCESS payment-result row.

This phase deliberately does not overwrite historical records or infer missing fields silently. Exact field-level parity across all historical workbooks remains a validation task.
