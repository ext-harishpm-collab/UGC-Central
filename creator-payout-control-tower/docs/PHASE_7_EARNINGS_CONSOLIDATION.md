# Phase 7 - Earnings ingestion and author-level payout preview

The system now recognizes the actual processed workbook pattern used by the supplied files:
- Show Book Mapping provides Book ID -> Show ID -> Author UID.
- Inc Final provides incentive rows with IP Type, Pay?, Book ID, Gross, TDS/Net fields.
- RS Final provides Revenue Share rows with IP Type, Pay?, Book ID, Gross, TDS/Net and Revenue%.
- N2A/A2A incentive rows are stored as excluded and never included in payout preview.
- Source Pay flags other than eligible/Yes are retained with an exclusion reason rather than silently removed.

The payout preview consolidates eligible Incentive + Revenue Share earnings at Author ID while retaining Book/Show/source lineage in the earning rows.

This is still a preview stage: recovery, contract-effective RS validation, deduction caps and final author net calculation must run through the full rules engine before a payout batch can be frozen.
