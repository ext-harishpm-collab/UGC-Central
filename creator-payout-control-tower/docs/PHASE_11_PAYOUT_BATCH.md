# Phase 11 - Payout batch, freeze and fixed UWT export

A payout preview can now be materialized as a draft payout batch. Batch status starts at DRAFT_QC_REQUIRED and cannot be frozen unless every payout line has QC PASS.

UWT export always uses the fixed 13-column layout. UWT imports update payment/ledger states and successful bank-account evidence only on SUCCESS results.

The batch layer preserves Author-level consolidation while payout_line_earnings retains the earning lineage needed to trace an author amount back to Book/Show reward rows.

Production still requires full QC and historical parity validation before freezing real money amounts.
